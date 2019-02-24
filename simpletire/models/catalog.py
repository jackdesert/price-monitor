from bs4 import BeautifulSoup
from concurrent import futures
from .fetcher import Fetcher
from .reading import Reading
from .util import Util
from .tire import Tire
import ipdb
import re
import traceback


class Catalog:
    class Meta:
        app_label = 'simpletire'

    SITEMAP = f'{Util.BASE_URL}/sitemap.xml'
    # Format: '205-55r16'
    # (There is only one hyphen)

    #WIDTH = 205
    #ASPECT = 55
    #WHEEL_DIAMETER = 16
    #TIRE_SIZE_REGEX= re.compile('205-55r16.*-tires$')
    #TIRE_SIZE_REGEX= re.compile(f'{WIDTH}-{ASPECT}z?r{WHEEL_DIAMETER}.*-tires$')

    TIRE_SIZE_REGEX= re.compile('\d{3}-\d{2}z?r\d{2}.*-tires$')

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
        output = []
        base_url_with_slash = f'{Util.BASE_URL}/'

        #print('SKIPPING SOME SITEMAPS')
        #self.sitemaps = self.sitemaps[3:]

        for sitemap in self.sitemaps:
            print(f'Fetching {sitemap}')
            fetcher = Fetcher(sitemap)
            if not fetcher.success:
                print(f'ERROR fetching particular sitemap: {sitemap}')
                continue
            print(f'Building BeautifulSoup Document for {sitemap}')
            doc = BeautifulSoup(fetcher.text, 'lxml')
            print('Building list of paths')
            for element in doc.find_all('url'):
                url = element.loc.text
                if self.TIRE_SIZE_REGEX.search(url):
                    path = url.replace(base_url_with_slash, '')
                    tire = existing_tires.get(path) or Tire(path=path)
                    output.append(tire)
            print(f'Done building')
        return output

    def _increment_fetch_count(self):
        with self.FETCH_COUNT_LOCK:
            self.fetch_count += 1
            return self.fetch_count

    def _fetch_tire_and_build_reading(self, tire):
        try:
            reading = tire.build_reading()
            return reading
        except Exception as ee:
            traceback.print_exc()
            return ee



    def fetch_and_write_pages(self):
        tire_ids_to_skip = Reading.tire_ids_with_readings_today()
        print(f'{len(tire_ids_to_skip)} tires already have readings today')

        tire_paths_to_skip = Util.recent_404_paths()
        print(f'{len(tire_paths_to_skip)} tires have 404 in last month')

        tires_to_fetch = []
        for tire in self._tires_from_sitemaps():
            if (tire.id not in tire_ids_to_skip) and (tire.path not in tire_paths_to_skip):
                tires_to_fetch.append(tire)

        #print('SKIPPING SOME TIRES')
        #tires_to_fetch = tires_to_fetch[0:10]

        num_tires_to_fetch = len(tires_to_fetch)
        print(f'{num_tires_to_fetch} tires will be fetched')

        # Using 10 processes loads my quad-core i7 processor (laptop)
        # to about 80% on each core, leaving room for other things
        executor = futures.ProcessPoolExecutor(max_workers=10)
        results = executor.map(self._fetch_tire_and_build_reading, tires_to_fetch)

        for index, result in enumerate(results):
            if isinstance(result, Reading):
                msg = f'Saved reading with tire_id {result.tire_id}'
                result.save()
            elif isinstance(result, Fetcher.Error404):
                msg = 'NOT SAVED: Error404'
            else:
                msg = f'NOT SAVING: {result}'

            print(f'{index}/{num_tires_to_fetch}. {msg}')

