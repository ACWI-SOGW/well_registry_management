"""
Tests for update_lookups management command
"""

from unittest.mock import patch, mock_open, MagicMock

from django.test import TestCase

from ..management.commands.update_lookups import Command
from ..models import AgencyLookup, AltitudeDatumLookup, CountryLookup, CountyLookup, HorizontalDatumLookup, \
    NatAqfrLookup,StateLookup, UnitsLookup

TEST_AGENCY_CSV = ('"AGENCY_CD","AGENCY_NM","AGENCY_MED"',
                   'MPCA,Minnesota Pollution Control Agency,MN Pollution Control Agency',
                   'ISWS,Illinois State Water Survey,IL State Water Survey')

TEST_ALTITUDE_DATUM_CSV = ('"ADATUM_CD","ADATUM_DESC"',
                           'NAVD88,North American Vertical Datum of 1988',
                           'NGVD29,National Geodetic Vertical Datum of 1929')

TEST_COUNTRY_CSV = ('"COUNTRY_CD","COUNTRY_NM"',
                    'AF,Afghanistan',
                    'AR,Argentina',
                    'US,United States of America')

TEST_HORIZONTAL_DATUM_CSV = ('"HDATUM_CD","HDATUM_DESC"',
                             'WGS84,World Geodetic System of 1984')

TEST_NAT_AQFR_CSV = ('"NAT_AQFR_CD","NAT_AQFR_DESC"',
                     'N100AKUNCD,Alaska unconsolidated-deposit aquifers',
                     'N100ALLUVL,Alluvial aquifers',
                     'N100BSNRGB,Basin and Range basin-fill aquifers')

TEST_UNITS_CSV = ('"UNIT_ID","UNIT_ABREV"',
                  '1,ft',
                  '2,cm')

TEST_STATE_CSV = ('"COUNTRY_CD","STATE_CD","STATE_NM"',
                  'US,"01",Alabama',
                  'US,"02",Alaska')

class TestUpdateLookups(TestCase):

    @staticmethod
    def get_open_mock(data):
        handle = MagicMock()
        handle.__enter__.return_value.__iter__.return_value = data
        handle.__exit__.return_value = False
        return handle

    @patch('builtins.open', spec=open)
    def test_loading_agency(self, mock_open):
        mock_open.side_effect = (
            self.get_open_mock(TEST_AGENCY_CSV),
            self.get_open_mock(TEST_ALTITUDE_DATUM_CSV),
            self.get_open_mock(TEST_COUNTRY_CSV),
            self.get_open_mock(TEST_HORIZONTAL_DATUM_CSV),
            self.get_open_mock(TEST_NAT_AQFR_CSV),
            self.get_open_mock(TEST_UNITS_CSV),
            self.get_open_mock(TEST_STATE_CSV)
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
