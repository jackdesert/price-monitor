
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from simpletire.models.tire import Tire
from simpletire.models.reading import Reading
from simpletire.models.catalog import Catalog

import pdb


class Command(BaseCommand):
    help = 'Fetches prices from simpletire.com and creates Readings'

    def handle(self, *args, **options):
        cat = Catalog()
        cat.fetch_and_write_pages()
        self.stdout.write('Done with fetch_and_write_pages')

