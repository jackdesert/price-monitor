
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from simpletire.models import Tire
from simpletire.models import Reading
from simpletire.models import Publisher

import pdb


class Command(BaseCommand):
    help = 'Fetches prices from simpletire.com and creates Readings'

    def handle(self, *args, **options):
        Publisher.publish()

