import pdb
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

    FETCH_PREPEND = 'fetched-'

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

    @classmethod
    def fetched_within_period(cls, path, period_seconds):
        # This method allows you to rate limit fetches to particular urls
        # by writing the url to redis with an expiration
        key = f'{cls.FETCH_PREPEND}{path}'

        # When ttl is -2, it means key not found
        # When ttl is -1, it means key present but has no expiration
        # When ttl is greater than 0, it means secons remaining
        ttl = cls.REDIS.ttl(key)

        if ttl > 0:
            print(f'{path} already fetched within period. ttl = {ttl / (24 * 3600)} days')
            return True
        cls.REDIS.set(key, 1, ex=period_seconds)
        print(f'{path} not fetched within period. Go ahead.')
        return False


