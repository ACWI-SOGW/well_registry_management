"""
Tests for registry admin module
"""
import datetime

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Group, Permission
from django.http import HttpRequest
from django.test import TestCase

from ..admin import RegistryAdminForm, RegistryAdmin, check_mark
from ..models import AgencyLookup, CountyLookup, StateLookup, Registry

from .lookups import create_lookup_data

class TestRegistryAdminForm(TestCase):

    def setUp(self):
        create_lookup_data()
        self.form_values = {
            'agency': AgencyLookup.objects.get(agency_cd='provider').id,
            'well_depth_units': 1,
            'altitude_datum': 'NAVD88',
            'altitude_units': 2,
            'horizontal_datum': 'NAD83',
            'nat_aqfr': 'N100AKUNCD',
            'country': 'US',
            'state': StateLookup.objects.get(state_cd='CA'),
            'county': CountyLookup.objects.get(county_cd='SF'),
            'site_no': '048043273',
            'site_name': 'blauer See',
            'dec_lat_va': 100.23,
            'dec_long_va': 49.23,
            'alt_va': 5.3,
            'local_aquifer_name': 'der Aquifer',
            'qw_sn_flag': 1,
            'qw_baseline_flag': 1,
            'qw_well_chars': 'NM',
            'qw_well_purpose': 'stuff',
            'wl_sn_flag': 1,
            'wl_baseline_flag': 1,
            'wl_well_chars': 'LK',
            'wl_well_purpose': 'well purpose',
            'qw_sys_name': 'die Fledermaus',
            'wl_sys_name': 'der Tiger',

            'display_flag': 0,

            'link': 'das Kaninchen',
            'wl_well_purpose_notes': 'der Dachshund',
            'qw_well_purpose_notes': 'der Krake'
        }

    def test_form_valid(self):
        form = RegistryAdminForm(data=self.form_values)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_agency(self):
        self.do_invalid_form('agency', 'ABCD')

    def test_form_with_invalid_horz_datum(self):
        self.do_invalid_form('horizontal_datum', 'NAD99')

    def test_form_with_invalid_alt_datum(self):
        self.do_invalid_form('altitude_datum', 'NAVD99')

    def test_form_with_invalid_nat_aquifer(self):
        self.do_invalid_form('nat_aqfr', 'NAD99')

    def test_form_with_invalid_country(self):
        self.do_invalid_form('country', 'FR')

    def test_form_with_invalid_state(self):
        self.do_invalid_form('state', 'CD')

    def test_form_with_invalid_county(self):
        self.do_invalid_form('county', 'SA')

    def test_form_with_invalid_well_depth_units(self):
        self.do_invalid_form('well_depth_units', 3)

    def test_form_with_invalid_alt_units(self):
        self.do_invalid_form('altitude_units', 4)

    def do_invalid_form(self, field, value):
        """Execute form validation failure test using the specified field and value"""
        self.form_values[field] = value
        form = RegistryAdminForm(data=self.form_values)
        self.assertFalse(form.is_valid())

        # verify that an error is thrown
        form_errors = form.errors.as_data()
        self.assertIsNotNone(form_errors.get(field))

class TestRegistryAdmin(TestCase):
    fixtures = ['test_registry.json', 'test_user.json']

    def setUp(self):
        self.superuser = User.objects.create_superuser('my_superuser')
        self.adwr_group = Group.objects.get(name='adwr')
        self.adwr_user = User.objects.create_user('adwr_user')
        self.adwr_user.groups.add(self.adwr_group)
        self.adwr_user.save()

        self.site = AdminSite()
        self.admin = RegistryAdmin(Registry, self.site)

    def test_site_id(self):
        reg_entry = Registry.objects.get(site_no='44445555',
                                         agency='ADWR')
        site_id = RegistryAdmin.site_id(reg_entry)

        self.assertEqual(site_id, "ADWR:44445555")

    def test_check_mark(self):
        check_html = check_mark(True)
        blank_html = check_mark(False)

        self.assertEqual(check_html, '&check;')
        self.assertEqual(blank_html, '')

    def test_get_queryset_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser
        qs = self.admin.get_queryset(request)

        self.assertEqual(qs.count(), 3)

    def test_get_queryset_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user
        qs = self.admin.get_queryset(request)

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.filter(agency='ADWR').count(), 1)

    def test_has_view_permission_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser

        self.assertTrue(self.admin.has_view_permission(request))
        self.assertTrue(self.admin.has_view_permission(request, Registry.objects.get(site_no='12345678')))

    def test_has_view_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_view_permission(request))
        self.assertTrue(self.admin.has_view_permission(request, Registry.objects.get(site_no='44445555')))
        self.assertFalse(self.admin.has_view_permission(request, Registry.objects.get(site_no='12345678')))

    def test_has_add_permission_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser

        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_add_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_change_permission_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser

        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_change_permission(request, Registry.objects.get(site_no='12345678')))

    def test_has_change_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_change_permission(request, Registry.objects.get(site_no='44445555')))
        self.assertFalse(self.admin.has_change_permission(request, Registry.objects.get(site_no='12345678')))


    def test_has_delete_permission_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser

        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request, Registry.objects.get(site_no='12345678')))

    def test_has_delete_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request, Registry.objects.get(site_no='44445555')))
        self.assertFalse(self.admin.has_delete_permission(request, Registry.objects.get(site_no='12345678')))

    def test_get_changeform_initial_data_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser

        self.assertEqual(self.admin.get_changeform_initial_data(request), {
            'agency': ''
        })

    def test_get_changeform_initial_data_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertEqual(self.admin.get_changeform_initial_data(request), {
            'agency': 'ADWR'
        })