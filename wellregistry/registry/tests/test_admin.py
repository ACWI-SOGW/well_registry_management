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

from ..admin import MonitoringLocationAdmin
from ..models import AgencyLookup, MonitoringLocation
from .fake_data import TEST_RDB, TEST_NO_WELL_DEPTH_RDB, TEST_STREAM_RDB


class TestMonitoringLocationAdmin(TestCase):
    fixtures = ['test_groups.json', 'test_user.json', 'test_agencies.json', 'test_monitoring_location.json']

    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser('my_superuser')
        self.adwr_group = Group.objects.get(name='adwr')
        self.usgs_group = Group.objects.get(name='usgs')

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
        self.adwr_user.is_staff = True
        self.adwr_user.save()

        self.usgs_user = get_user_model().objects.create_user('usgsuser')
        self.usgs_user.groups.add(self.usgs_group)
        self.usgs_user.user_permissions.set([
            self.add_permission,
            self.view_permission,
            self.change_permission,
            self.delete_permission
        ])
        self.usgs_user.is_staff = True
        self.usgs_user.save()

        self.site = AdminSite()
        self.admin = MonitoringLocationAdmin(MonitoringLocation, self.site)

    def test_site_id(self):
        reg_entry = MonitoringLocation.objects.get(site_no='44445555',
                                                   agency='ADWR')
        site_id = MonitoringLocationAdmin.site_id(reg_entry)

        self.assertEqual(site_id, "ADWR:44445555")

    def test_save_model_new_monitoring_location_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user
        monitoring_location = MonitoringLocation.objects.create(site_no='11111111',
                                                                agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, monitoring_location, None, None)

        saved_monitoring_location = MonitoringLocation.objects.get(site_no='11111111')
        self.assertEqual(saved_monitoring_location.insert_user, self.adwr_user)
        self.assertEqual(saved_monitoring_location.update_user, self.adwr_user)
        self.assertEqual(saved_monitoring_location.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

    def test_save_model_new_monitoring_location_with_super_user(self):
        request = HttpRequest()
        request.user = self.superuser
        monitoring_location = MonitoringLocation.objects.create(site_no='11111111',
                                                                agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, monitoring_location, None, None)

        saved_monitoring_location = MonitoringLocation.objects.get(site_no='11111111')
        self.assertEqual(saved_monitoring_location.insert_user, self.superuser)
        self.assertEqual(saved_monitoring_location.update_user, self.superuser)
        self.assertEqual(saved_monitoring_location.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

    def test_save_model_existing_monitoring_location_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.superuser
        monitoring_location = MonitoringLocation.objects.create(site_no='11111111',
                                                                agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, monitoring_location, None, None)

        saved_monitoring_location = MonitoringLocation.objects.get(site_no='11111111')
        saved_monitoring_location.site_name = 'A site'
        request.user = self.adwr_user
        self.admin.save_model(request, saved_monitoring_location, None, None)
        saved_monitoring_location = MonitoringLocation.objects.get(site_no='11111111')

        self.assertEqual(saved_monitoring_location.insert_user, self.superuser)
        self.assertEqual(saved_monitoring_location.update_user, self.adwr_user)
        self.assertEqual(saved_monitoring_location.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

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

    def test_changelist_view_with_usgs_user(self):
        client = Client()
        client.force_login(self.usgs_user)
        resp = client.get('/registry/admin/registry/monitoringlocation/')
        self.assertTrue(resp.context['show_fetch_from_nwis_view'])

    def test_changelist_view_with_adwr_user(self):
        client = Client()
        client.force_login(self.adwr_user)
        resp = client.get('/registry/admin/registry/monitoringlocation/')
        self.assertFalse(resp.context['show_fetch_from_nwis_view'])


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
