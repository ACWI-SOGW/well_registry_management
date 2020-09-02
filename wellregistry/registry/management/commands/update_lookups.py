"""
Command to load data from CSV's into the lookup tables
"""

import csv
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from ...models import CountryLookup

INITIAL_DATA_DIR = os.path.join(settings.BASE_DIR, 'registry/management/commands/initial_data/')

class Command(BaseCommand):
    help = 'Loads the lookup data from csv files'

    def _update_country_lookups(self):
        data_src = os.path.join(INITIAL_DATA_DIR, 'country.csv')
        with default_storage.open(data_src, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # skip the header row
            for country_cd, country_nm in csvreader:
                CountryLookup.objects.update_or_create(
                    country_cd=country_cd,
                    defaults={'country_cd': country_cd, 'country_nm': country_nm}
                )

    def handle(self, *args, **options):
        self._update_country_lookups()
        self.stdout.write('Successfully updated lookups')
