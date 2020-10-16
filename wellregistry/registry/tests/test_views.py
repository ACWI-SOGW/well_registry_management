"""
Tests for the registry  views module
"""

from django.test import RequestFactory, TestCase

from ..views import BasePage, MonitoringLocationsListView, status_check


class TestBasePage(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_base_page(self):
        req = self.factory.get('/registry')
        resp = BasePage.as_view()(req)
        self.assertEqual(resp.status_code, 200)


class TestMonitoringLocationsListView(TestCase):
    fixtures = ['test_agencies.json', 'test_altitude_datum.json', 'test_counties.json',
                'test_countries.json', 'test_horizontal_datum.json', 'test_nat_aquifer.json',
                'test_states.json', 'test_units.json', 'test_groups.json', 'test_monitoring_location.json',
                'test_user.json']

    def setUp(self):
        self.factory = RequestFactory()

    def test_all_monitoring_locations(self):
        req = self.factory.get('/registry/monitoring-locations/?format=json')
        resp = MonitoringLocationsListView.as_view()(req)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 3)

    def test_display_flag_true_monitoring_locations(self):
        req = self.factory.get('/registry/monitoring-locations/?format=json&display_flag=true')
        resp = MonitoringLocationsListView.as_view()(req)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['site_no'], '11112222')

    def test_display_flag_false_monitoring_locations(self):
        req = self.factory.get('/registry/monitoring-locations/?format=json&display_flag=false')
        resp = MonitoringLocationsListView.as_view()(req)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 2)
        self.assertIn(resp.data['results'][0]['site_no'], ['12345678', '44445555'])
        self.assertIn(resp.data['results'][1]['site_no'], ['12345678', '44445555'])


class TestStatusCheck(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_base_page(self):
        # TEST ACTION
        req = self.factory.get('/registry/status')

        # VALUE EXTRACT
        resp = status_check(req)
        index = str(resp.content).index('{"status": "up"}')

        # ASSERTIONS
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(index, 2)
