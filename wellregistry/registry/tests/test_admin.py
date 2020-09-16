"""
Tests for registry admin module
"""
import io

from requests_mock import Mocker

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import TestCase, Client

from ..admin import MonitoringLocationAdmin, MonitoringLocationAdminForm
from ..models import AgencyLookup, MonitoringLocation
from .fake_data import TEST_RDB, TEST_NO_WELL_DEPTH_RDB, TEST_STREAM_RDB


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


class TestFetchFromNwisView(TestCase):
    FETCH_URL = '/registry/admin/registry/monitoringlocation/fetch_from_nwis/'
    fixtures = ['test_agencies', 'test_countries.json', 'test_states.json', 'test_counties.json',
                'test_horizontal_datum.json', 'test_altitude_datum.json', 'test_nat_aquifer.json']

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create(username='testuser', password='12345', is_staff=True,
                                                    is_superuser=True)
        self.client.force_login(self.user)

        self.usgs_agency = AgencyLookup.objects.get(agency_cd='USGS')

    def test_get_view(self):
        resp = self.client.get(self.FETCH_URL)
        content = resp.content.decode("utf-8")
        self.assertIn('id_site_no', content)
        self.assertNotIn('id_overwrite', content)

    @Mocker()
    def test_post_with_new_site_no(self, mock_request):
        test_rdb = io.BytesIO(TEST_RDB)
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        resp = self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })
        self.assertTrue(MonitoringLocation.objects.filter(site_no='443053094591001', agency=self.usgs_agency).exists())
        monitoring_location = MonitoringLocation.objects.get(site_no='443053094591001', agency=self.usgs_agency)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, f'/registry/admin/registry/monitoringlocation/{monitoring_location.id}/change/')

    @Mocker()
    def test_post_with_existing_site(self, mock_request):
        test_rdb = io.BytesIO(TEST_RDB)

        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })

        resp2 = self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(resp2.context['show_overwrite'])

    @Mocker()
    def test_post_with_no_overwrite(self, mock_request):
        test_rdb = io.BytesIO(TEST_RDB)
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })
        monitoring_location = MonitoringLocation.objects.get(site_no='443053094591001', agency=self.usgs_agency)
        monitoring_location.site_name = 'New Name'
        monitoring_location.save()
        resp2 = self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001',
            'overwrite': 'n'
        })

        self.assertEqual(resp2.status_code, 302)
        self.assertRedirects(resp2, f'/registry/admin/registry/monitoringlocation/{monitoring_location.id}/change/')
        self.assertEqual(MonitoringLocation.objects.get(site_no='443053094591001', agency=self.usgs_agency).site_name,
                         'New Name')

    @Mocker()
    def test_post_with_overwrite(self, mock_request):
        test_rdb = io.BytesIO(TEST_RDB)
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })
        monitoring_location = MonitoringLocation.objects.get(site_no='443053094591001', agency=self.usgs_agency)
        monitoring_location.site_name = 'New Name'
        monitoring_location.save()

        test_rdb = io.BytesIO(TEST_RDB)
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        resp2 = self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001',
            'overwrite': 'y'
        })

        self.assertEqual(resp2.status_code, 302)
        self.assertRedirects(resp2, f'/registry/admin/registry/monitoringlocation/{monitoring_location.id}/change/')
        self.assertNotEqual(
            MonitoringLocation.objects.get(site_no='443053094591001', agency=self.usgs_agency).site_name,
            'New Name')

    @Mocker()
    def test_post_with_stream_site(self, mock_request):
        test_stream_site_rdb = io.BytesIO(TEST_STREAM_RDB)
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_stream_site_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        resp = self.client.post(self.FETCH_URL, {
            'site_no': '543053094591001'
        })
        self.assertFalse(MonitoringLocation.objects.filter(site_no='543053094591001', agency=self.usgs_agency).exists())
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Site is not a Well or Spring', resp.context['request_response'])

    @Mocker()
    def test_post_with_site_with_no_well_depth(self, mock_request):
        test_stream_site_rdb = io.BytesIO(TEST_NO_WELL_DEPTH_RDB)
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, body=test_stream_site_rdb,
                         headers={'Content-Type': 'text/plain;charset=UTF-8'})
        resp = self.client.post(self.FETCH_URL, {
            'site_no': '643053094591001'
        })
        self.assertFalse(MonitoringLocation.objects.filter(site_no='643053094591001', agency=self.usgs_agency).exists())
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Site is missing a well depth', resp.context['request_response'])

    @Mocker()
    def test_site_not_found(self, mock_request):
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, status_code=404)
        resp = self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['request_response'],
                         'No site exists for 443053094591001')

    @Mocker()
    def test_service_failure(self, mock_request):
        mock_request.get(settings.NWIS_SITE_SERVICE_ENDPOINT, status_code=500)
        resp = self.client.post(self.FETCH_URL, {
            'site_no': '443053094591001'
        })

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['request_response'],
                         'Service request to NWIS failed with status 500')
