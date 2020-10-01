"""
Tests for the registry admin custom bulk upload view
"""

from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest
from django.test import TestCase, Client

from ...models import AgencyLookup, MonitoringLocation
from ...admin.bulk_upload import BulkUploadView


class TestBulkUploadView(TestCase):
    URL = '/registry/admin/registry/monitoringlocation/bulk_upload/'
    fixtures = ['test_agencies', 'test_countries.json', 'test_states.json', 'test_counties.json',
                'test_horizontal_datum.json', 'test_altitude_datum.json', 'test_nat_aquifer.json',
                'test_units.json']

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create(username='testuser', password='12345', is_staff=True,
                                                    is_superuser=True)
        self.client.force_login(self.user)

        self.view = BulkUploadView()

        request = HttpRequest()
        request.META['SCRIPT_NAME'] = ''
        request.user = self.user
        self.view.request = request

    def test_get_view(self):
        resp = self.client.get(self.URL)
        content = resp.content.decode('utf-8')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<input id="id_file"', content)
        self.assertNotIn('<ul class="errorlist">', content)

    def test_post_valid_ml(self):
        TEST_ML = b'ADWR,Kb32-13,Dummy record,39.035721,-75.72704,NAD27,Survey,0.1 m,58.54,ft,NAVD88,\
Survey,0.01m,N100GLCIAL,Federalsburg,1234,United States of America,Michigan,St. Francis County,192,ft,\
WELL,CONFINED,No,Yes,Yes,Background,Surveillance,Dedicated Monitoring/Observation,Just cuz,\
Michigan Groundwater Network,Yes,Yes,Background,Surveillance,Dedicated Monitoring/Observation,,\
Michigan Groundwater Network,http://www.dgs.udel.edu/data'

        file = SimpleUploadedFile('test.csv', b'HEADER LINE\n' + TEST_ML, content_type='text/csv')
        self.view.request.FILES['file'] = file
        resp = self.view.post(self.view.request)

        self.assertEqual(resp.status_code, 302)

    def test_post_view_file_invalid_ml(self):
        TEST_ML = b'ADWR,Kb32-13,Dummy record,39.035721,-75.72704,NAD27,Survey,0.1 m,58.54,ft,NAVD88,\
        Survey,0.01m,N100GLCIAL,Federalsburg,1234,United States of America,Michigan,,192,ft,\
        WELL,CONFINED,No,Yes,Yes,Background,Surveillance,Dedicated Monitoring/Observation,Just cuz,\
        Michigan Groundwater Network,Yes,Yes,Background,Surveillance,Dedicated Monitoring/Observation,,\
        Michigan Groundwater Network,http://www.dgs.udel.edu/data'

        file = SimpleUploadedFile('test.csv', b'HEADER LINE\n' + TEST_ML, content_type='text/csv')
        self.view.request.FILES['file'] = file
        resp = self.view.post(self.view.request)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('class="errorlist"', resp.content.decode())

    def test_post_view_file_invalid_with_multi_field_issue(self):
        TEST_ML = b'ADWR,Kb32-13,Dummy record,39.035721,-75.72704,NAD27,Survey,0.1 m,58.54,ft,NAVD88,\
                Survey,0.01m,S100NATLCP,Federalsburg,1234,United States of America,Delaware,St. Francis County,192,,\
                WELL,CONFINED,No,Yes,Yes,\
                Background,Surveillance,Dedicated Monitoring/Observation,Just cuz,Michigan Groundwater Network,Yes,Yes,\
                Background,Surveillance,Dedicated Monitoring/Observation,,Michigan Groundwater Network,\
                http://www.dgs.udel.edu/data'

        file = SimpleUploadedFile('test.csv', b'HEADER LINE\n' + TEST_ML, content_type='text/csv')
        self.view.request.FILES['file'] = file
        resp = self.view.post(self.view.request)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('class="errorlist"', resp.content.decode())

    def test_post_view_file_invalid_number_of_columns(self):
        file = SimpleUploadedFile('test.csv', b'HEADER LINE\n1234,USGS,', content_type='text/csv')
        self.view.request.FILES['file'] = file
        resp = self.view.post(self.view.request)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('class="errorlist"', resp.content.decode())

