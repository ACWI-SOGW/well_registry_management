"""
Tests for the registry admin custom fetch from NWIS view
"""
import io

from requests_mock import Mocker

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ...models import AgencyLookup, MonitoringLocation
from ..fake_data import TEST_RDB, TEST_NO_WELL_DEPTH_RDB, TEST_STREAM_RDB


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
