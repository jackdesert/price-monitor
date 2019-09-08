from bs4 import BeautifulSoup
import pdb
import re
from .fetcher import Fetcher

class PriceChecker:

    class UndefinedProperty(Exception):
        '''Price, InStock, and Name are undefined because you were unable to fetch'''

    UTQG_REGEX = re.compile(r'UTQG: (\d+)')

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

    @property
    def utqg(self):
        self._require_success('utqg')

        for li in self.doc.find('ul', 'speclist').findAll('li'):
            match = re.search(self.UTQG_REGEX, li.text)
            if match:
                return int(match[1])


    def _require_success(self, property_name):
        if not self.success:
            raise self.UndefinedProperty(property_name)

