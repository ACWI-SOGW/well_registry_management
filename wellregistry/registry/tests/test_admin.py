"""
Tests for registry admin module
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import TestCase

from ..admin import MonitoringLocationAdmin, MonitoringLocationAdminForm
from ..models import AgencyLookup, MonitoringLocation


class TestRegistryFormAdmin(TestCase):
    fixtures = ['test_agencies.json', 'test_countries.json', 'test_counties.json',
                'test_states.json', 'test_altitude_datum.json',
                'test_horizontal_datum.json', 'test_nat_aquifer.json', 'test_units.json']

    def setUp(self):
        self.form_data = {
            'display_flag': False,
            'agency': 'USGS',
            'state': '39',
            'country': 'US',
            'county': '171',
            'site_no': '1234567',
            'site_name': 'My test site',
            'dec_lat_va': '98.456',
            'dec_long_va': '-84.567',
            'horizontal_datum': 'NAD27',
            'alt_va': '2',
            'altitude_units': '1',
            'altitude_datum': 'NAD83',
            'nat_aqfr': 'N100GLCIAL',
            'site_type': 'WELL',
            'aqfr_type': 'UNCONFINED',
            'well_depth': '4.2',
            'well_depth_units': '1',
            'wl_sn_flag': False,
            'wl_baseline_flag': False,
            'qw_sn_flag': False,
            'qw_baseline_flag': False,
            'wl_well_chars': '',
            'ql_well_chars': ''
        }

    def test_valid_when_display_flag_false(self):
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_when_site_no_blank(self):
        self.form_data['site_no'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['site_no'] = '     '
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_site_name_blank(self):
        self.form_data['site_name'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['site_name'] = '     '
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_state_blank(self):
        self.form_data['state'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_county_blank(self):
        self.form_data['county'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_latitude_blank(self):
        self.form_data['dec_lat_va'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['dec_lat_va'] = '     '
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_longitude_blank(self):
        self.form_data['dec_long_va'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['dec_long_va'] = '     '
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_horizontal_datum_blank(self):
        self.form_data['horizontal_datum'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_altitude_blank(self):
        self.form_data['alt_va'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['alt_va'] = '     '
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_altitude_units_blank(self):
        self.form_data['altitude_units'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_altitude_datum_blank(self):
        self.form_data['altitude_datum'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_national_aquifer_blank(self):
        self.form_data['nat_aqfr'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_site_type_blank(self):
        self.form_data['site_type'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_valid_when_display_flag_true_sn_flags_false(self):
        self.form_data['display_flag'] = True
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_when_site_type_well_and_aquifer_type_blank(self):
        self.form_data['site_type'] = 'WELL'
        self.form_data['aqfr_type'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_depth_unit_blank(self):
        self.form_data['well_depth'] = '5'
        self.form_data['well_depth_units'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_depth_unit_not_blank(self):
        self.form_data['well_depth'] = ''
        self.form_data['well_depth_units'] = '1'
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_valid_when_display_flag_true_and_wl_sn_flags_true(self):
        self.form_data['display_flag'] = True
        self.form_data['wl_sn_flag'] = True
        self.form_data['wl_well_purpose'] = 'Other'
        self.form_data['wl_well_type'] = 'Trend'
        form = MonitoringLocationAdminForm(self.form_data)

        self.assertTrue(form.is_valid())

    def test_invalid_when_display_flag_true_and_wl_sn_flag_true(self):
        self.form_data['display_flag'] = True
        self.form_data['wl_sn_flag'] = True
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['wl_well_purpose'] = ''
        self.form_data['wl_well_type'] = 'Trend'
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['wl_well_purpose'] = 'Other'
        self.form_data['wl_well_type'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_display_flag_true_and_wl_sn_flag_true_and_wl_baseline_true(self):
        self.form_data['display_flag'] = True
        self.form_data['wl_sn_flag'] = True
        self.form_data['wl_well_type'] = 'Trend'
        self.form_data['wl_well_purpose'] = 'Other'
        self.form_data['wl_baseline_flag'] = True
        self.form_data['wl_well_chars'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_valid_when_display_flag_true_and_qw_sn_flags_true(self):
        self.form_data['display_flag'] = True
        self.form_data['qw_sn_flag'] = True
        self.form_data['qw_well_purpose'] = 'Other'
        self.form_data['qw_well_type'] = 'Trend'
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_when_display_flag_true_and_qw_sn_flag_true(self):
        self.form_data['display_flag'] = True
        self.form_data['qw_sn_flag'] = True
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['qw_well_purpose'] = ''
        self.form_data['qw_well_type'] = 'Trend'
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

        self.form_data['qw_well_purpose'] = 'Other'
        self.form_data['qw_well_type'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_when_display_flag_true_and_qw_sn_flag_true_and_qw_baseline_true(self):
        self.form_data['display_flag'] = True
        self.form_data['qw_sn_flag'] = True
        self.form_data['qw_well_type'] = 'Trend'
        self.form_data['qw_well_purpose'] = 'Other'
        self.form_data['qw_baseline_flag'] = True
        self.form_data['qw_well_chars'] = ''
        form = MonitoringLocationAdminForm(self.form_data)
        self.assertFalse(form.is_valid())


class TestRegistryAdmin(TestCase):
    fixtures = ['test_groups.json', 'test_user.json', 'test_agencies.json', 'test_monitoring_location.json']

    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser('my_superuser')
        self.adwr_group = Group.objects.get(name='adwr')
        self.add_permission = Permission.objects.get(codename='add_monitoringlocation')
        self.view_permission = Permission.objects.get(codename='view_monitoringlocation')
        self.change_permission = Permission.objects.get(codename='change_monitoringlocation')
        self.delete_permission = Permission.objects.get(codename='delete_monitoringlocation')

        self.adwr_user = get_user_model().objects.create_user('adwruser')
        self.adwr_user.groups.add(self.adwr_group)
        self.adwr_user.user_permissions.set([
            self.add_permission,
            self.view_permission,
            self.change_permission,
            self.delete_permission
        ])
        self.adwr_user.save()

        self.site = AdminSite()
        self.admin = MonitoringLocationAdmin(MonitoringLocation, self.site)

    def test_site_id(self):
        reg_entry = MonitoringLocation.objects.get(site_no='44445555',
                                                   agency='ADWR')
        site_id = MonitoringLocationAdmin.site_id(reg_entry)

        self.assertEqual(site_id, "ADWR:44445555")

    def test_save_model_new_registry_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user
        registry = MonitoringLocation.objects.create(site_no='11111111',
                                                     agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, registry, None, None)

        saved_registry = MonitoringLocation.objects.get(site_no='11111111')
        self.assertEqual(saved_registry.insert_user, self.adwr_user)
        self.assertEqual(saved_registry.update_user, self.adwr_user)
        self.assertEqual(saved_registry.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

    def test_save_model_new_registry_with_super_user(self):
        request = HttpRequest()
        request.user = self.superuser
        registry = MonitoringLocation.objects.create(site_no='11111111',
                                                     agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, registry, None, None)

        saved_registry = MonitoringLocation.objects.get(site_no='11111111')
        self.assertEqual(saved_registry.insert_user, self.superuser)
        self.assertEqual(saved_registry.update_user, self.superuser)
        self.assertEqual(saved_registry.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

    def test_save_model_existing_registry_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.superuser
        registry = MonitoringLocation.objects.create(site_no='11111111',
                                                     agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, registry, None, None)

        saved_registry = MonitoringLocation.objects.get(site_no='11111111')
        saved_registry.site_name = 'A site'
        request.user = self.adwr_user
        self.admin.save_model(request, saved_registry, None, None)
        saved_registry = MonitoringLocation.objects.get(site_no='11111111')

        self.assertEqual(saved_registry.insert_user, self.superuser)
        self.assertEqual(saved_registry.update_user, self.adwr_user)
        self.assertEqual(saved_registry.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

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
        self.assertTrue(self.admin.has_view_permission(request, MonitoringLocation.objects.get(site_no='12345678')))

    def test_has_view_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_view_permission(request))
        self.assertTrue(self.admin.has_view_permission(request, MonitoringLocation.objects.get(site_no='44445555')))
        self.assertFalse(self.admin.has_view_permission(request, MonitoringLocation.objects.get(site_no='12345678')))

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
        self.assertTrue(self.admin.has_change_permission(request, MonitoringLocation.objects.get(site_no='12345678')))

    def test_has_change_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_change_permission(request, MonitoringLocation.objects.get(site_no='44445555')))
        self.assertFalse(self.admin.has_change_permission(request, MonitoringLocation.objects.get(site_no='12345678')))

    def test_has_delete_permission_with_superuser(self):
        request = HttpRequest()
        request.user = self.superuser

        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request, MonitoringLocation.objects.get(site_no='12345678')))

    def test_has_delete_permission_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user

        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request, MonitoringLocation.objects.get(site_no='44445555')))
        self.assertFalse(self.admin.has_delete_permission(request, MonitoringLocation.objects.get(site_no='12345678')))
