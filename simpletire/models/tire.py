from django.db import models
import ipdb
from .util import Util
from .price_checker import PriceChecker
from .fetcher import Fetcher
import simpletire.models.reading as reading


class Tire(models.Model):
    path = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    class Meta():
        # This index acts as a unique constraint (probably not required for speed)
        index_together = ['path']
        app_label = 'simpletire'


    PENNIES_PER_DOLLAR = 100


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
        if self.name != checker.name:
            if self._persisted:
                print(f'Renaming "{self.name}" to "{checker.name}"')
            else:
                print(f'New tire: "{checker.name}"')

            self.name = checker.name
            self.save()


        #print(f'Building new reading for {today_string} and {self.name}')
        new_reading = reading.Reading(tire=self,
                                      price_pennies=price_pennies,
                                      date=today_string,
                                      in_stock=in_stock)

        return new_reading

    def readings(self):
        return self.reading_set(manager='_default_manager').all()

    def __repr__(self):
        return f'Tire({self.name})'

    @property
    def _persisted(self):
        return bool(self.id)

    #@classmethod
    #def find_or_initialize_by_path(cls, path):
    #    try:
    #        tire = cls.objects.get(path=path)
    #    except cls.DoesNotExist:
    #        tire = Tire(path=path)
    #    return tire


