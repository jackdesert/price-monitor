from bs4 import BeautifulSoup
from datetime import date as newdate
from django.db import models
import ipdb
import re
import requests
import sys



class Catalog:

    BASE_URL = 'https://simpletire.com'
    SITEMAP = f'{BASE_URL}/sitemap.xml'
    # Format: '205-55r16'
    # (There is only one hyphen)
    WIDTH = 205
    ASPECT = 55
    WHEEL_DIAMETER = 16
    #TIRE_SIZE_REGEX= re.compile('205-55r16.*-tires$')
    TIRE_SIZE_REGEX= re.compile(f'{WIDTH}-{ASPECT}z?r{WHEEL_DIAMETER}.*-tires$')

    def __init__(self):
        self.sitemaps = []
        self._set_sitemaps()

    def _set_sitemaps(self):
        fetcher = Fetcher(self.SITEMAP)
        if not fetcher.success:
            print('\nERROR fetching sitemaps\n')
            return

        doc = BeautifulSoup(fetcher.text, 'lxml')
        for element in doc.find_all('sitemap'):
            url = element.loc.text
            self.sitemaps.append(url)
        print('Found Sitemaps:')
        for ss in self.sitemaps:
            print(f'  {ss}')
        print('')

    def fetch_and_write_pages(self):
        base_url_with_slash = f'{self.BASE_URL}/'
        for sitemap in self.sitemaps:
            print(f'Fetching {sitemap}')
            fetcher = Fetcher(sitemap)
            if not fetcher.success:
                print(f'ERROR fetching particular sitemap: {sitemap}')
                continue
            doc = BeautifulSoup(fetcher.text, 'lxml')
            for element in doc.find_all('url'):
                url = element.loc.text
                if self.TIRE_SIZE_REGEX.search(url):
                    path = url.replace(base_url_with_slash, '')
                    tire = Tire.find_or_initialize_by_path(path)
                    tire.fetch_and_store_current_price()

                    #page = Page(url)
                    #page.write()

class Fetcher:
    URL_404 = 'https://simpletire.com/errors/error400'
    HEADERS = { 'User-Agent': 'Price-Monitor' }
    TIMEOUT_SECONDS = 1

    class Error404(Exception):
        '''404 Not Found'''

    def __init__(self, url):
        self.url = url
        self.text = ''
        self._fetch()

    @property
    def success(self):
        return bool(self.text)

    def _fetch(self):
        try:
            page = requests.get(self.url,
                                timeout=self.TIMEOUT_SECONDS,
                                headers=self.HEADERS)
        except Exception as ee:
            exception_name = type(ee).__name__
            msg = f'ERROR: {exception_name} accessing {self.url}\n'
            sys.stderr.write(msg)
            return

        # If page is not found, it gets redirected to URL_404
        if page.url == self.URL_404:
            print(f'ERROR 404 {self.url} *******************************')
            raise self.Error404(self.url)

        self.text = page.text


class Tire(models.Model):
    path = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)

    PENNIES_PER_DOLLAR = 100


    def fetch_and_store_current_price(self):
        today_string = newdate.today().strftime('%F')
        preexisting = self.reading_set(manager='_default_manager').filter(date=today_string)
        if preexisting.exists():
            print(f'Reading already exists for {today_string} and {self.name}')
            return

        url = f'{Catalog.BASE_URL}/{self.path}'
        try:
            checker = PriceChecker(url)
        except Fetcher.Error404:
            return

        if not checker.success:
            return

        try:
            price_float = float(checker.price)
        except ValueError:
            print(f'ERROR: Skipping {self.name} because price not parseable: "{checker.price}"')
            return

        price_pennies = round(price_float * self.PENNIES_PER_DOLLAR)
        in_stock = checker.in_stock
        if self.name != checker.name:
            if self._persisted:
                print(f'Renaming "{self.name}" to "{checker.name}"')
            else:
                print(f'New tire: "{checker.name}"')

            self.name = checker.name
            self.save()

        new_reading = Reading(tire=self,
                              price_pennies=price_pennies,
                              date=today_string,
                              in_stock=in_stock)
        new_reading.save()

        print(f'Creating new reading for {today_string} and {self.name}')

    def readings(self):
        return self.reading_set(manager='_default_manager').all()

    def __repr__(self):
        return f'Tire({self.name})'

    @property
    def _persisted(self):
        return bool(self.id)

    @classmethod
    def find_or_initialize_by_path(cls, path):
        try:
            tire = cls.objects.get(path=path)
        except cls.DoesNotExist:
            tire = Tire(path=path)
        return tire


class PriceChecker:

    class UndefinedProperty(Exception):
        '''Price, InStock, and Name are undefined because you were unable to fetch'''

    def __init__(self, url):
        self.url = url
        self.fetcher = Fetcher(url)
        self.doc = BeautifulSoup(self.fetcher.text, 'lxml')

    @property
    def success(self):
        return self.fetcher.success

    @property
    def price(self):
        self._require_success('price')

        for item in self.doc.find_all('span', {'itemprop':'price'}):
            if not 'price_before_round' in item.get('id'):
                return item.text

    @property
    def in_stock(self):
        self._require_success('in_stock')

        if 'out of stock' in self.doc.text.lower():
            return False
        else:
            return True


    @property
    def name(self):
        self._require_success('name')

        element = self.doc.find(id='product-name')
        if not element:
            return
        return element.text

    def _require_success(self, property_name):
        if not self.success:
            raise self.UndefinedProperty(property_name)





class Reading(models.Model):
    class Meta:
        unique_together = ('tire', 'date')


    tire = models.ForeignKey(Tire, on_delete=models.CASCADE)
    date = models.DateField()
    price_pennies = models.PositiveIntegerField()
    in_stock = models.BooleanField()

    def __repr__(self):
        return (f'Reading(tire=<some_tire>\n'
                f"        date='{self.date}'\n"
                f'        price_pennies={self.price_pennies}\n'
                f'        in_stock={self.in_stock})')



if __name__ == '__main__':
    eye = Eyeglass()
    eye.fetch_and_write_pages()

