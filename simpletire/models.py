from bs4 import BeautifulSoup
from datetime import date as newdate
from django.db import models
import boto3
import csv
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
        today_string = Util.today_string()
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


class StatsPresenter:
    PENNIES_PER_DOLLAR = 100
    DEFAULT_SORT_KEY = 'mean'

    @classmethod
    def tire_stats(cls):
        tires = Tire.objects.raw(cls._query_postgres())
        output = []
        for tire in tires:
            tire_dict = dict(id=tire.id,
                             name=tire.name,
                             path=tire.path,
                             num_readings=tire.num_readings,
                             min=tire.min_pennies / cls.PENNIES_PER_DOLLAR,
                             max=tire.max_pennies / cls.PENNIES_PER_DOLLAR,
                             mean=tire.mean_pennies / cls.PENNIES_PER_DOLLAR,
                             std=(tire.std_pennies or 0) / cls.PENNIES_PER_DOLLAR,
                             current=tire.current_pennies / cls.PENNIES_PER_DOLLAR)
            output.append(tire_dict)
        return output

    @classmethod
    def tire_stats_sorted(cls, sort_key, reverse):
        stats = cls.tire_stats()

        if sort_key not in stats[0].keys():
            sort_key = cls.DEFAULT_SORT_KEY

        key = lambda x: x[sort_key]
        stats.sort(key=key, reverse=reverse)
        return stats


    @classmethod
    def _query_postgres(cls):
        return '''
        SELECT t.id, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
          JOIN
            (
             SELECT
                tire_id,
                count(*) as num_readings,
                avg(price_pennies)  AS mean_pennies,
                min(price_pennies)  AS min_pennies,
                max(price_pennies)  AS max_pennies,
                stddev_samp(price_pennies) AS std_pennies
              FROM simpletire_reading
              WHERE in_stock = 't'
              GROUP BY tire_id
            ) AS stats
            ON t.id = stats.tire_id

          JOIN
            (
              SELECT DISTINCT ON (tire_id) tire_id, date, price_pennies as current_pennies
              FROM simpletire_reading
              ORDER BY tire_id, date DESC
             ) AS currents
             ON stats.tire_id = currents.tire_id;'''

    @classmethod
    def _query_generic(cls):
        return '''
        SELECT t.id, name, path, num_readings, min_pennies, max_pennies, mean_pennies, std_pennies, current_pennies FROM simpletire_tire t
          JOIN
            (
             SELECT
                tire_id,
                count(*) as num_readings,
                avg(price_pennies)  AS mean_pennies,
                min(price_pennies)  AS min_pennies,
                max(price_pennies)  AS max_pennies,
                stddev_samp(price_pennies) AS std_pennies
              FROM simpletire_reading
              WHERE in_stock = 't'
              GROUP BY tire_id
            ) AS stats
            ON t.id = stats.tire_id

          JOIN
            (
            SELECT tire_id, price_pennies as current_pennies, date
            FROM
              (
                SELECT tire_id,
                       price_pennies,
                       date,
                       max(date) OVER (PARTITION BY tire_id) as max_date
                FROM simpletire_reading
                ORDER BY tire_id, date DESC
               ) AS currents_temp WHERE date = max_date
            ) AS currents
           ON stats.tire_id = currents.tire_id;'''

    @classmethod
    def _query_prestodb(cls):
        # PrestoDB uses true and false as booleans instead of 't' and 'f'
        return cls._query_generic().replace("= 't'", "= true")


class Util:
    @classmethod
    def today_string(cls):
        return newdate.today().strftime('%F')


class Publisher:
    ACCESS_KEY_ID = 'AKIAJAWJQPXLMDRR34TQ'
    SECRET_ACCESS_KEY = '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'

    TIRE_FILE_TEMP_LOCAL = '/tmp/tires.csv'
    READINGS_FILE_TEMP_LOCAL = '/tmp/readings.csv'
    BUCKET_NAME_TIRES = 'bip-price-monitor-tires'
    BUCKET_NAME_READINGS = 'bip-price-monitor-readings'
    TIRE_FILE_REMOTE = 'tires.csv'
    DELIMITER = '|'

    @classmethod
    def publish(cls):
        cls.write_tires_to_csv()
        cls.write_todays_readings_to_csv()

        s3 = boto3.client('s3', aws_access_key_id=cls.ACCESS_KEY_ID,
                                aws_secret_access_key=cls.SECRET_ACCESS_KEY)

        s3.upload_file(cls.TIRE_FILE_TEMP_LOCAL,
                       cls.BUCKET_NAME_TIRES,
                       cls.TIRE_FILE_REMOTE)

        s3.upload_file(cls.READINGS_FILE_TEMP_LOCAL,
                       cls.BUCKET_NAME_READINGS,
                       cls._readings_file_remote())

    @classmethod
    def write_tires_to_csv(cls):
        with open(cls.TIRE_FILE_TEMP_LOCAL, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=cls.DELIMITER)
            for tire in Tire.objects.all():
                row = [tire.id, tire.name, tire.path]
                writer.writerow(row)

    @classmethod
    def write_todays_readings_to_csv(cls):
        with open(cls.READINGS_FILE_TEMP_LOCAL, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=cls.DELIMITER)
            for reading in Reading.objects.filter(date=Util.today_string()):
                row = [reading.id, reading.tire_id, reading.date, reading.price_pennies, reading.in_stock]
                writer.writerow(row)

    @classmethod
    def _readings_file_remote(cls):
        today_string = Util.today_string()
        return f'readings-{today_string}'

    # Column names are only here for pasting into Amazon Athena
    # during table definition
    #
    @classmethod
    def _tire_column_names(cls):
        '''
        id int,
        name string,
        path string
        '''

    @classmethod
    def _reading_column_names(cls):
        '''
        id int,
        tire_id int,
        date string,
        price_pennies int,
        in_stock boolean
        '''


if __name__ == '__main__':
    eye = Eyeglass()
    eye.fetch_and_write_pages()

