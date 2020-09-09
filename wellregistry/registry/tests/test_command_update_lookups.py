"""
Tests for update_lookups management command
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase

from ..management.commands.update_lookups import Command
from ..models import AgencyLookup, AltitudeDatumLookup, CountryLookup, CountyLookup, HorizontalDatumLookup, \
    NatAqfrLookup, StateLookup, UnitsLookup

TEST_AGENCY_CSV = ['"AGENCY_CD","AGENCY_NM","AGENCY_MED"',
                   'MPCA,Minnesota Pollution Control Agency,MN Pollution Control Agency',
                   'ISWS,Illinois State Water Survey,IL State Water Survey']

TEST_ALTITUDE_DATUM_CSV = ['"ADATUM_CD","ADATUM_DESC"',
                           'NAVD88,North American Vertical Datum of 1988',
                           'NGVD29,National Geodetic Vertical Datum of 1929']

TEST_COUNTRY_CSV = ['"COUNTRY_CD","COUNTRY_NM"',
                    'AF,Afghanistan',
                    'AR,Argentina',
                    'US,United States of America']

TEST_HORIZONTAL_DATUM_CSV = ['"HDATUM_CD","HDATUM_DESC"',
                             'WGS84,World Geodetic System of 1984']

TEST_NAT_AQFR_CSV = ['"NAT_AQFR_CD","NAT_AQFR_DESC"',
                     'N100AKUNCD,Alaska unconsolidated-deposit aquifers',
                     'N100ALLUVL,Alluvial aquifers',
                     'N100BSNRGB,Basin and Range basin-fill aquifers']

TEST_UNITS_CSV = ['"UNIT_ID","UNIT_ABREV"',
                  '1,ft',
                  '2,cm']

TEST_STATE_CSV = ['"COUNTRY_CD","STATE_CD","STATE_NM"',
                  'US,"01",Alabama',
                  'US,"02",Alaska']

TEST_COUNTY_CSV = ['"COUNTRY_CD","STATE_CD","COUNTY_CD","COUNTY_NM"',
                   'US,"01","001",Autauga County',
                   'US,"01","003",Baldwin County',
                   'US,"02","068",Denali Borough']


class TestUpdateLookups(TestCase):
    @staticmethod
    def get_open_mock(data):
        handle = MagicMock()
        handle.__enter__.return_value.__iter__.return_value = data
        handle.__exit__.return_value = False
        return handle

    @patch('builtins.open', spec=open)
    def test_loading_lookups(self, mock_open):
        mock_open.side_effect = (
            self.get_open_mock(TEST_AGENCY_CSV),
            self.get_open_mock(TEST_ALTITUDE_DATUM_CSV),
            self.get_open_mock(TEST_COUNTRY_CSV),
            self.get_open_mock(TEST_HORIZONTAL_DATUM_CSV),
            self.get_open_mock(TEST_NAT_AQFR_CSV),
            self.get_open_mock(TEST_UNITS_CSV),
            self.get_open_mock(TEST_STATE_CSV),
            self.get_open_mock(TEST_COUNTY_CSV)
        )

        command = Command()
        command.handle()

        self.assertEqual(AgencyLookup.objects.count(), 2)
        self.assertEqual(AltitudeDatumLookup.objects.count(), 2)
        self.assertEqual(CountryLookup.objects.count(), 3)
        self.assertEqual(HorizontalDatumLookup.objects.count(), 1)
        self.assertEqual(NatAqfrLookup.objects.count(), 3)
        self.assertEqual(UnitsLookup.objects.count(), 2)
        self.assertEqual(StateLookup.objects.count(), 2)
        self.assertEqual(CountyLookup.objects.count(), 3)

    @patch('builtins.open', spec=open)
    def test_updating_lookups(self, mock_open):
        mock_open.side_effect = (
            self.get_open_mock(TEST_AGENCY_CSV),
            self.get_open_mock(TEST_ALTITUDE_DATUM_CSV),
            self.get_open_mock(TEST_COUNTRY_CSV),
            self.get_open_mock(TEST_HORIZONTAL_DATUM_CSV),
            self.get_open_mock(TEST_NAT_AQFR_CSV),
            self.get_open_mock(TEST_UNITS_CSV),
            self.get_open_mock(TEST_STATE_CSV),
            self.get_open_mock(TEST_COUNTY_CSV)
        )
        command = Command()
        command.handle()

        new_agency_csv = TEST_AGENCY_CSV.copy()
        new_agency_csv.append('MN_DNR,Minnesota Department of Natural Resources,MN Dept. of Natural Resources')
        new_altitude_csv = TEST_ALTITUDE_DATUM_CSV.copy()
        new_altitude_csv[1] = 'NAVD88,North American Vertical Datum of 2088'
        new_state_csv = TEST_STATE_CSV.copy()
        new_state_csv.append('US,"04",Arizona')
        new_county_csv = TEST_COUNTY_CSV.copy()
        new_county_csv.append('US,"04","003",Cochise County')
        mock_open.side_effect = (
            self.get_open_mock(new_agency_csv),
            self.get_open_mock(new_altitude_csv),
            self.get_open_mock(TEST_COUNTRY_CSV),
            self.get_open_mock(TEST_HORIZONTAL_DATUM_CSV),
            self.get_open_mock(TEST_NAT_AQFR_CSV),
            self.get_open_mock(TEST_UNITS_CSV),
            self.get_open_mock(new_state_csv),
            self.get_open_mock(new_county_csv)
        )
        command = Command()
        command.handle()

        self.assertEqual(AgencyLookup.objects.count(), 3)
        self.assertEqual(AltitudeDatumLookup.objects.count(), 2)
        self.assertEqual(AltitudeDatumLookup.objects.get(adatum_cd='NAVD88').adatum_desc,
                         'North American Vertical Datum of 2088')
        self.assertEqual(CountryLookup.objects.count(), 3)
        self.assertEqual(HorizontalDatumLookup.objects.count(), 1)
        self.assertEqual(NatAqfrLookup.objects.count(), 3)
        self.assertEqual(UnitsLookup.objects.count(), 2)
        self.assertEqual(StateLookup.objects.count(), 3)
        self.assertEqual(CountyLookup.objects.count(), 4)
