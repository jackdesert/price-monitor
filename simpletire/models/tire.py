from datetime import datetime
from datetime import timedelta
from django.db import models
import pdb
import re
from .util import Util
from .price_checker import PriceChecker
from .fetcher import Fetcher
#from simpletire.models import reading as my_reading
from simpletire.models import reading


class Tire(models.Model):
    path = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    section_width  = models.SmallIntegerField()
    wheel_diameter = models.SmallIntegerField()
    aspect_ratio   = models.SmallIntegerField()
    utqg           = models.SmallIntegerField(null=True)

    SPACE = ' '
    DIMENSIONS = {'section_width', 'aspect_ratio', 'wheel_diameter'}
    OPERATORS = dict(section_width='>=', aspect_ratio='IN', wheel_diameter='=')
    ASPECT_RATIO_SPACING = 5
    DIMENSION_CHAR_COUNT = dict(section_width=3, aspect_ratio=2, wheel_diameter=2)
    MM_PER_INCH = 25.4

    class Meta():
        # This index acts as a unique constraint (probably not required for speed)
        index_together = ['path']
        app_label = 'simpletire'


    PENNIES_PER_DOLLAR = 100
    MIN_FETCH_PERIOD_SECONDS = 7 * 24 * 3600


    def build_reading(self):
        today_string = Util.today_string()

        # No need to check if reading exists for today because we
        # check that before this method is called

        url = f'{Util.BASE_URL}/{self.path}'
        try:
            checker = PriceChecker(url)
        except Fetcher.Error404 as ee:
            print(f'Storing as 404: {self.path}')
            Util.store_path_as_404(self.path)
            return ee

        if not checker.success:
            return 'not checker success'

        try:
            price_float = float(checker.price)


        except (TypeError, ValueError) as ee:
            # TypeError happens when checker.price is None
            # ValueError happens when checker.price is a non-numeric string
            print(f'ERROR: Skipping {self.name} because price not parseable: "{checker.price}"')

            return ee

        price_pennies = round(price_float * self.PENNIES_PER_DOLLAR)
        in_stock = checker.in_stock

        if not checker.name:
            return f'Not creating tire {url} because name is NULL'

        if not self._persisted and not in_stock:
            return f'Not creating tire {url} because not in stock'

        if (self.name != checker.name) or (self.utqg != checker.utqg):
            if self._persisted:
                print(f'Renaming "{self.name}" with utqg {self.utqg} to "{checker.name}" with utqg {checker.utqg}')
            else:
                print(f'Creating tire: "{checker.name}"')



            self.name = checker.name
            self.utqg = checker.utqg
            self.set_dimensions()
            self.save()


        #print(f'Building new reading for {today_string} and {self.name}')
        new_reading = reading.Reading(tire=self,
                                      price_pennies=price_pennies,
                                      date=today_string,
                                      in_stock=in_stock)

        return new_reading

    def readings(self):
        return self.reading_set(manager='_default_manager').all()

    def ok_to_fetch(self):
        # Indicates whether it is time to fetch this tire
        if not self.last_fetch_at:
            return True
        line_in_sand = datetime.now() - timedelta(days=self.MIN_DAYS_BETWEEN_FETCHES)
        ready = self.last_fetch_at < line_in_sand
        if ready:
            print('OK to Fetch')
        else:
            print(f'NOT FETCHING because last_fetch_at is {self.last_fetch_at}')

        return ready

    def __repr__(self):
        return f'Tire({self.name})'

    @property
    def size(self):
        return f'{self.section_width}/{self.aspect_ratio}r{self.wheel_diameter}'

    @property
    def diameter(self):
        aspect_ratio_decimal = self.aspect_ratio / 100
        section_width_inches = self.section_width / self.MM_PER_INCH
        sidewall_height_inches = section_width_inches * aspect_ratio_decimal
        return self.wheel_diameter + 2 * sidewall_height_inches

    @property
    def _persisted(self):
        return bool(self.id)

    def set_dimensions(self):
        if not self.path:
            return

        matches = re.search(Util.TIRE_SIZE_REGEX, self.path)
        self.section_width  = int(matches[1])
        self.aspect_ratio   = int(matches[2])
        self.wheel_diameter = int(matches[3])

    def fetched_within_period(self):
        return Util.fetched_within_period(self.path, self.MIN_FETCH_PERIOD_SECONDS)

    @classmethod
    def valid_dimensions(cls, dimensions):
        for dimension, value in dimensions.items():
            if len(str(value)) != cls.DIMENSION_CHAR_COUNT[dimension]:
                return False
        return True

    @classmethod
    def filter_by_size(cls, **dimensions):
        sql  = 'SELECT * FROM simpletire_tire '
        sql += cls.sql_filter(**dimensions)
        return cls.objects.raw(sql)


    @classmethod
    def sql_filter(cls, **dimensions):

        # Make sure only expected dimensions are passed in
        assert not set(dimensions.keys()) - cls.DIMENSIONS

        statements = []
        conjunction = 'WHERE'
        for dimension, value in dimensions.items():
            if not value:
                continue
            op = cls.OPERATORS[dimension]
            if dimension == 'aspect_ratio':
                value = f'({value}, {value + cls.ASPECT_RATIO_SPACING}, {value - cls.ASPECT_RATIO_SPACING})'
            statements.append(f'{conjunction} {dimension} {op} {value}')
            conjunction = 'AND'

        return cls.SPACE.join(statements)


