"""
Tests for registry admin module
"""
import datetime

from django.test import TestCase

from ..admin import RegistryAdminForm, RegistryAdmin, check_mark
from ..models import CountryLookup, Registry


class TestRegistryAdminForm(TestCase):

    def setUp(self):
        CountryLookup.objects.create(
            country_cd='US',
            country_nm='United States'
        )
        self.form_values = {
            'agency_cd': 'ZYX',
            'well_depth_units': 1,
            'alt_datum_cd': 'NAVD88',
            'alt_units': 2,
            'horz_datum': 'NAD83',
            'nat_aquifer_cd': 'AQ CODE',
            'country_cd': 'US',  # the primary key of the only entry in the country lookup table
            'state_cd': 'CA',
            'county_cd': 'SF',
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

    def test_form_with_valid_country(self):
        form = RegistryAdminForm(data=self.form_values)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_country(self):
        self.form_values['country_cd'] = 'FR'
        form = RegistryAdminForm(data=self.form_values)
        self.assertFalse(form.is_valid())

        # verify that an error is thrown for the country code
        form_errors = form.errors.as_data()
        self.assertIsNotNone(form_errors.get('country_cd'))


class TestRegistryAdmin(TestCase):

    def test_site_id(self):
        # SETUP
        reg_entry = Registry()
        reg_entry.agency_cd = 'provider'
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
