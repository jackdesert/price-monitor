
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from simpletire.models.stats_presenter import StatsPresenter

import pdb


class Command(BaseCommand):
    help = 'Load aggregates'

    def handle(self, *args, **options):
        StatsPresenter.load()
        self.stdout.write('done')

