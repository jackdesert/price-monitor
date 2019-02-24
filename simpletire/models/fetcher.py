import ipdb
import requests
import sys

class Fetcher:

    URL_404 = 'https://simpletire.com/errors/error400'
    HEADERS = { 'User-Agent': 'Price-Monitor' }
    TIMEOUT_SECONDS = 10

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
