from bs4 import BeautifulSoup
from concurrent import futures
from .fetcher import Fetcher
from .reading import Reading
from .util import Util
from .tire import Tire
from .stats_presenter import StatsPresenter
from time import sleep
import pdb
import re
import traceback
import io

class UrlParser:
    # Find urls in text using minimal amount of memory
    # (BeautifulSoup creates large objects

    URL_REGEX = re.compile(r'<loc>(http.*)</loc>')

    # generator function
    @classmethod
    def urls_from_blob(cls, blob_of_text):
        buffer = io.StringIO(blob_of_text)
        line = 'start'
        while line:
            # When empty, readlin() returns empty string
            line = buffer.readline()
            match = cls.URL_REGEX.search(line)
            if match:
                yield match[1]


class Catalog:

    SITEMAP = f'{Util.BASE_URL}/sitemap.xml'
    SMALL_BATCH_SIZE = 4
    DELAY_SECONDS = 8
    # Format: '205-55r16'
    # (There is only one hyphen)

    def __init__(self):
        self.sitemaps = []
        self._set_sitemaps()

    def _set_sitemaps(self):
        fetcher = Fetcher(self.SITEMAP)
        if not fetcher.success:
            print('\nERROR fetching top-level sitemap\n')
            return

        doc = BeautifulSoup(fetcher.text, 'lxml')
        for element in doc.find_all('sitemap'):
            url = element.loc.text
            self.sitemaps.append(url)
        print('Found Sitemaps:')
        for ss in self.sitemaps:
            print(f'  {ss}')
        print('')

    def _dictionary_of_existing_tires(self):
        return { tire.path: tire for tire in Tire.objects.all() }


    def _tires_from_sitemaps(self):
        existing_tires = self._dictionary_of_existing_tires()
        base_url_with_slash = f'{Util.BASE_URL}/'

        #print('SKIPPING SOME SITEMAPS')
        #self.sitemaps = self.sitemaps[3:]

        for sitemap in self.sitemaps:
            print(f'Fetching {sitemap}')
            fetcher = Fetcher(sitemap)
            if not fetcher.success:
                print(f'ERROR fetching particular sitemap: {sitemap}')
                continue

            for url in UrlParser.urls_from_blob(fetcher.text):
                if Util.TIRE_SIZE_REGEX.search(url):
                    path = url.replace(base_url_with_slash, '')
                    tire = existing_tires.get(path) or Tire(path=path)
                    yield tire
            print(f'Done yielding tires for {sitemap}')
            StatsPresenter.load()

    def _tires_to_fetch(self):
        tire_ids_to_skip = Reading.tire_ids_with_readings_today()
        print(f'{len(tire_ids_to_skip)} tires already have readings today')

        tire_paths_to_skip = Util.recent_404_paths()
        print(f'{len(tire_paths_to_skip)} tires have 404 in last month')

        for tire in self._tires_from_sitemaps():
            if (tire.id not in tire_ids_to_skip) and (tire.path not in tire_paths_to_skip):
                yield tire

    def _increment_fetch_count(self):
        with self.FETCH_COUNT_LOCK:
            self.fetch_count += 1
            return self.fetch_count




    def _save_result(self, result, index):
        if isinstance(result, Reading):
            msg = f'Saved reading with tire_id {result.tire_id}'
            result.save()
        elif isinstance(result, Fetcher.Error404):
            msg = 'NOT SAVED: Error404'
        else:
            msg = f'NOT SAVING: {result}'
        print(f'{index}. {msg}\n')



    def _fetch_tire_and_build_reading(self, tire):
        # For MULTI_THREADED only
        # This prints the stack track but lets other things keep processing
        try:
            reading = tire.build_reading()
            return reading
        except Exception as ee:
            traceback.print_exc()
            return ee


    # THREADED BULK
    # Builds up the whole list of tires to fetch
    # Then builds up a list of results
    # And finally saves each result
    # Consumes about 400 MB
    # Saves about 4 records per second
    def fetch_and_write_pages_threaded_bulk(self):
        executor = futures.ThreadPoolExecutor(max_workers=4)
        results = executor.map(self._fetch_tire_and_build_reading, self._tires_to_fetch())

        for index, result in enumerate(results):
            self._save_result(result, index)



    # THREADED IN SMALL BATCHES
    # Only uses threads to fetch small batches of things at a time
    # Still uses generators so there is no need for a full list of all tires
    # or all results
    # Consumes about 150MB
    # Saves about 2.5 records per second
    def fetch_and_write_pages_threaded_small_batches(self):
        executor = futures.ThreadPoolExecutor(max_workers=self.SMALL_BATCH_SIZE)
        tires = []
        for main_index, tire in enumerate(self._tires_to_fetch()):
            tires.append(tire)
            if len(tires) == self.SMALL_BATCH_SIZE:
                results = executor.map(self._fetch_tire_and_build_reading, tires)
                for index, result in enumerate(results):
                    self._save_result(result, main_index + index)
                tires.clear()


    # SYNCHRONOUS, SINGLE_THREADED, ENFORCES DELAY and MIN_DAYS_BETWEEN_FETCHES
    # Consumes about 140MB
    # Saves about 1.2 records per second
    def fetch_and_write_pages(self):
        for index, tire in enumerate(self._tires_to_fetch()):
            if not tire.fetched_within_period():
                result = tire.build_reading()
                self._save_result(result, index)
                sleep(self.DELAY_SECONDS)
            if index % 1000 == 0:
                # Every N cycles, load the data
                StatsPresenter.load()
