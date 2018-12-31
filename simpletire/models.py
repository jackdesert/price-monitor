from django.db import models
import requests
import pdb
from datetime import date as newdate


SITE = 'https://simpletire.com/'

def get_text(url):
    try:
        text = requests.get(url, timeout=1).text
    except Exception as ee:
        exception_name = type(ee).__name__
        sys.stderr.write(f'ERROR: {exception_name} accessing {url}\n')
        text = ''
    return text


class Tire(models.Model):
    path = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)

    BASE_URL = 'https://simpletire.com'
    PENNIES_PER_DOLLAR = 100

    @classmethod
    def find_or_create_by_path(cls, path):
        try:
            tire = cls.objects.get(path=path)
        except cls.DoesNotExist:
            tire = Tire(path=path)
            tire.save()
        return tire

    def fetch_and_store_current_price(self):
        url = f'{SITE}{self.path}'
        checker = PriceChecker(url)
        price_string = checker.price
        price_pennies = round(float(price_string) * self.PENNIES_PER_DOLLAR)
        in_stock = checker.in_stock
        name = checker.name
        if self.name != name:
            self.name = name
            self.save()
            print(f'Setting name to {name}')

        today_string = newdate.today().strftime('%F')
        try:
            self.reading_set(manager='_default_manager').get(date=today_string)
            print(f'Reading already exists for {today_string} and {name}')
        except Reading.DoesNotExist:
            new_reading = Reading(tire=self,
                                  price=price_pennies,
                                  date=today_string,
                                  in_stock=in_stock)
            pdb.set_trace()
            new_reading.save()
            print(f'Creating new reading for {today_string} and {name}')







class Reading(models.Model):
    class Meta:
        unique_together = ('tire', 'date')


    tire = models.ForeignKey(Tire, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.PositiveSmallIntegerField()
    in_stock = models.BooleanField()

from bs4 import BeautifulSoup
import ipdb
import re
import sys
from datetime import date

class PriceChecker:

    def __init__(self, url):
        self.url = url
        text = get_text(self.url)
        self.doc = BeautifulSoup(text, 'lxml')

    @property
    def price(self):
        for item in self.doc.find_all('span', {'itemprop':'price'}):
            if not 'price_before_round' in item.get('id'):
                return item.text

    @property
    def in_stock(self):
        if 'out of stock' in self.doc.text.lower():
            return False
        else:
            return True


    @property
    def name(self):
        element = self.doc.find(id='product-name')
        if not element:
            return
        return element.text





class Catalog:

    SITE = 'https://simpletire.com/'
    SITEMAP = f'{SITE}sitemap.xml'
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
        text = get_text(self.SITEMAP)
        doc = BeautifulSoup(text, 'lxml')
        for element in doc.find_all('sitemap'):
            url = element.loc.text
            print(f'SITEMAP: {url}')
            self.sitemaps.append(url)

    def fetch_and_write_pages(self):
        for sitemap in self.sitemaps:
            text = get_text(sitemap)
            doc = BeautifulSoup(text, 'lxml')
            for element in doc.find_all('url'):
                url = element.loc.text
                if self.TIRE_SIZE_REGEX.search(url):
                    path = url.replace(self.SITE, '')
                    tire = Tire.find_or_create_by_path(path)
                    tire.fetch_and_store_current_price()
                    pdb.set_trace()

                    #page = Page(url)
                    #page.write()








if __name__ == '__main__':
    eye = Eyeglass()
    eye.fetch_and_write_pages()

