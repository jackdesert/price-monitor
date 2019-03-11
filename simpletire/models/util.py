import ipdb
import redis
import re
from datetime import date as newdate


class Util:
    # Constants used by all classes
    BASE_URL = 'https://simpletire.com'
    TIRE_SIZE_REGEX = re.compile('(\d{3})-(\d{2})z?r(\d{2}).*-tires$')
    ###############################


    REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)
    RECENT_PREPEND = 'simpletire-404--'
    DURATION_OF_404_IN_SECONDS = 3600 * 24 * 30 # One month

    @classmethod
    def today_string(cls):
        return newdate.today().strftime('%F')

    @classmethod
    def recent_404_paths(cls):
        output = set()
        cursor = 0
        while True:
            cursor, results = cls.REDIS.scan(cursor, match=f'{cls.RECENT_PREPEND}*')
            for rr in results:
                key = rr.decode()
                path = key.replace(cls.RECENT_PREPEND, '')
                output.add(path)
            if cursor == 0:
                break

        return output

    @classmethod
    def store_path_as_404(cls, path):
        # If a 404 is returned, don't bother checking that path again for another month
        key = cls._404_key(path)
        cls.REDIS.set(key,
                      '404', # This value could be anything
                      ex=cls.DURATION_OF_404_IN_SECONDS)

    @classmethod
    def _404_key(cls, path):
        return f'{cls.RECENT_PREPEND}{path}'


