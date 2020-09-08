"""
Command to load data from CSV's into the lookup tables
"""

import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import CountryLookup, StateLookup, CountyLookup, NatAqfrLookup, AltitudeDatumLookup, \
    HorizontalDatumLookup, UnitsLookup, AgencyLookup

INITIAL_DATA_DIR = os.path.join(settings.BASE_DIR, 'registry/management/commands/initial_data/')


class Command(BaseCommand):
    help = 'Loads the lookup data from csv files'

    def _update_simple_lookups(self, filename, model, field_names):
        """
        Update the model with the contents of filename. Existing fields are updated
        thereby retaining their primary key value.
        :param filename: Name of the csv file in INITIAL_DATA_DIR containing lookups to be updated.
                         The first column is assumed to be the unique id.
        :param model: Lookup model
        :param field_names: tuple of fields in model. The order of the tuple should reflect the order of
                            columns in filename
        :return:
        """
        data_src = os.path.join(INITIAL_DATA_DIR, filename)
        with open(data_src, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # skip the header row
            for values in csvreader:
                model.objects.update_or_create(
                    **{field_names[0]: values[0]}, defaults=dict(zip(field_names, values))
                )
        self.stdout.write(f'Successfully updated registry.{model._meta.db_table}')

    def _update_state_lookups(self):
        """
        Update state lookup table from data in a CSV.
        Foreign keys are set using records in the country lookup table.

        """
        data_src = os.path.join(INITIAL_DATA_DIR, 'state.csv')
        with open(data_src, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for country_cd, state_cd, state_nm in csvreader:
                country = CountryLookup.objects.get(country_cd=country_cd)
                state = StateLookup.objects.update_or_create(
                    country_cd=country, state_cd=state_cd,
                    defaults={'country_cd': country, 'state_cd': state_cd, 'state_nm': state_nm}
                )

        self.stdout.write(f'Successfully updated registry.{StateLookup._meta.db_table}')

    def _update_county_lookups(self):
        """
        Load county lookup table from data in a CSV.
        Foreign keys are set using records in the country and state lookup tables.
        """
        data_src = os.path.join(INITIAL_DATA_DIR, 'county.csv')
        with open(data_src, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for country_cd, state_cd, county_cd, county_nm in csvreader:
                try:
                    country = CountryLookup.objects.get(country_cd=country_cd)
                    state = StateLookup.objects.get(state_cd=state_cd, country_cd=country_cd)
                except (CountryLookup.DoesNotExist, StateLookup.DoesNotExist):
                    continue
                else:
                    county = CountyLookup.objects.update_or_create(
                        county_cd=county_cd,
                        country_cd=country,
                        state_id=state,
                        defaults={'country_cd': country,
                                  'state_id': state,
                                  'county_cd': county_cd,
                                  'county_nm': county_nm}
                    )
        self.stdout.write(f'Successfully updated registry.{CountyLookup._meta.db_table}')
        
    def handle(self, *args, **options):
        self._update_simple_lookups('agency.csv', AgencyLookup, field_names=['agency_cd', 'agency_nm', 'agency_med'])
        self._update_simple_lookups('altitude_datums.csv', AltitudeDatumLookup,
                                    field_names=['adatum_cd', 'adatum_desc'])
        self._update_simple_lookups('country.csv', CountryLookup, field_names=['country_cd', 'country_nm'])
        self._update_simple_lookups('horizontal_datums.csv', HorizontalDatumLookup,
                                    field_names=['hdatum_cd', 'hdatum_desc'])
        self._update_simple_lookups('nat_aqfr.csv', NatAqfrLookup, field_names=['nat_aqfr_cd', 'nat_aqfr_desc'])
        self._update_simple_lookups('units.csv', UnitsLookup, field_names=['unit_id', 'unit_desc'])
        self._update_state_lookups()
        self._update_county_lookups()

        self.stdout.write('Successfully updated all lookups')
