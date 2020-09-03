"""
Tests for update_lookups management command
"""

from unittest.mock import patch, mock_open, MagicMock

from django.test import TestCase

from ..management.commands.update_lookups import Command
from ..models import AgencyLookup, AltitudeDatumLookup

TEST_AGENCY_CSV = ('"AGENCY_CD","AGENCY_NM","AGENCY_MED"',
                   'MPCA,Minnesota Pollution Control Agency,MN Pollution Control Agency',
                   'ISWS,Illinois State Water Survey,IL State Water Survey')

TEST_ALTITUDE_DATUM_CSV = ('"ADATUM_CD","ADATUM_DESC"',
    'NAVD88,North American Vertical Datum of 1988',
    'NGVD29,National Geodetic Vertical Datum of 1929')

class TestUpdateLookups(TestCase):

    @patch('builtins.open', spec=open)
    def test_loading_new_data(self, mock_open):
        handle1 = MagicMock()
        handle1.__enter__.return_value.__iter__.return_value = TEST_AGENCY_CSV
        handle1.__exit__.return_value = False
        handle2 = MagicMock()
        handle2.__enter__.return_value.__iter__.return_value = TEST_ALTITUDE_DATUM_CSV
        handle2.__exit__.return_value = False
        mock_open.side_effect = (handle1, handle2)

        command = Command()
        command.handle()
        self.assertEqual(AgencyLookup.objects.count(), 2)
        self.assertEqual(AltitudeDatumLookup.objects.count(), 2)
