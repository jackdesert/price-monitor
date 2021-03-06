from django.db import models
import pdb
from .util import Util

# Import module instead of "from x import X" syntax
# to avoid circular dependencies
#from simpletire.models import tire as my_tire
from simpletire.models import tire


class Reading(models.Model):
    class Meta:
        unique_together = ('tire', 'date')
        app_label = 'simpletire'


    tire = models.ForeignKey(tire.Tire, on_delete=models.CASCADE)
    date = models.DateField()
    price_pennies = models.PositiveIntegerField()
    in_stock = models.BooleanField()

    @classmethod
    def tire_ids_with_readings_today(cls):
        today_string = Util.today_string()
        return { reading.tire_id for reading in cls.objects.filter(date=today_string) }

    @classmethod
    def most_recent(cls):
        return cls.objects.order_by('-date')[0]

    def __repr__(self):
        return (f'Reading(tire=<some_tire>\n'
                f"        date='{self.date}'\n"
                f'        price_pennies={self.price_pennies}\n'
                f'        in_stock={self.in_stock})')


