"""
Tests for registry admin module
"""
import datetime

from django.test import TestCase

from ..admin import RegistryAdminForm, RegistryAdmin, check_mark
from .lookups import LookupData
from ..models import AgencyLovLookup, CountyLookup, StateLookup, Registry

class TestRegistryAdminForm(TestCase):

    def setUp(self):
        LookupData.create()
        self.form_values = {
            'agency_cd': 'provider',
            'well_depth_units': 1,
            'alt_datum_cd': 'NAVD88',
            'alt_units': 2,
            'horz_datum': 'NAD83',
            'nat_aquifer_cd': 'N100AKUNCD',
            'country_cd': 'US',
            'state_cd': StateLookup.objects.get(state_cd = 'CA'),
            'county_cd': CountyLookup.objects.get(county_cd = 'SF'),
            'agency_nm': 'Die Katze',
            'agency_med': 'Der Hund',
            'site_no': '048043273',
            'site_name': 'blauer See',
            'dec_lat_va': 100.23,
            'dec_long_va': 49.23,
            'alt_va': 5.3,
            'nat_aqfr_desc': 'An Aquifer',
            'local_aquifer_name': 'der Aquifer',
            'qw_sn_flag': 1,
            'qw_baseline_flag': 1,
            'qw_well_chars': 'NM',
            'qw_well_purpose': 'stuff',
            'wl_sn_flag': 1,
            'wl_baseline_flag': 1,
            'wl_well_chars': 'LK',
            'wl_well_purpose': 'well purpose',
            'data_provider': 'das Unterseeboot',
            'qw_sys_name': 'die Fledermaus',
            'wl_sys_name': 'der Tiger',
            'pk_siteid': 'blah',
            'display_flag': 0,
            'wl_data_provider': 'der Eisbar',
            'qw_data_provider': 'der Falke',
            'lith_data_provider': 'die Ente',
            'const_data_provider': 'der Haifisch',
            'well_depth': 17.8,
            'link': 'das Kaninchen',
            'wl_well_purpose_notes': 'der Dachshund',
            'qw_well_purpose_notes': 'der Krake',
            'insert_user_id': 'my user',
            'update_user_id': 'my mser',
            'wl_well_type': 'DKE',
            'qw_well_type': 'KAL',
            'local_aquifer_cd': 'local aquifer',
            'review_flag': 'L',
            'site_type': 'Spring',
            'aqfr_char': 'blah',
            'horz_method': 'Horizontal Method',
            'horz_acy': 'Horizontal Accuracy',
            'alt_method': 'Alt Method',
            'alt_acy': 'Alt Accuracy',
            'insert_date': datetime.datetime(2020, 6, 18, 21, 55, 9),
            'update_date': datetime.datetime(2020, 6, 18, 21, 55, 10)
        }

    def test_form_valid(self):
        form = RegistryAdminForm(data=self.form_values)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_agency(self):
        self.do_invalid_form('agency_cd', 'ABCD')

    def test_form_with_invalid_horz_datum(self):
        self.do_invalid_form('horz_datum', 'NAD99')

    def test_form_with_invalid_alt_datum(self):
        self.do_invalid_form('alt_datum_cd', 'NAVD99')

    def test_form_with_invalid_nat_aquifer(self):
        self.do_invalid_form('nat_aquifer_cd', 'NAD99')

    def test_form_with_invalid_country(self):
        self.do_invalid_form('country_cd', 'FR')

    def test_form_with_invalid_state(self):
        self.do_invalid_form('state_cd', 'CD')

    def test_form_with_invalid_county(self):
        self.do_invalid_form('county_cd', 'SA')

    def test_form_with_invalid_well_depth_units(self):
        self.do_invalid_form('well_depth_units', 3)

    def test_form_with_invalid_alt_units(self):
        self.do_invalid_form('alt_units', 4)

    def do_invalid_form(self, field, value):
        self.form_values[field] = value
        form = RegistryAdminForm(data=self.form_values)
        self.assertFalse(form.is_valid())

        # verify that an error is thrown
        form_errors = form.errors.as_data()
        self.assertIsNotNone(form_errors.get(field))

class TestRegistryAdmin(TestCase):
    def setUp(self):
        LookupData.create()

    def test_site_id(self):
        # SETUP
        reg_entry = Registry()
        reg_entry.agency_cd = AgencyLovLookup.objects.get(agency_cd = 'provider')
        reg_entry.site_no = '12345'

        # TEST ACTION
        site_id = RegistryAdmin.site_id(reg_entry)

        # ASSERTION
        self.assertEqual(site_id, "provider:12345")

    def test_check_mark(self):
        # SETUP
        true_flag = True
        false_flag = False

        # TEST ACTION
        check_html = check_mark(true_flag)
        blank_html = check_mark(false_flag)

        # ASSERTION
        self.assertEqual(check_html, '&check;')
        self.assertEqual(blank_html, '')
