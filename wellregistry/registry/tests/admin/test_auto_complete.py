"""
Tests for admin.monitoring_location for Autocomplete module
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase

class TestAutoCompleteView(TestCase):
    # pylint: disable=too-many-instance-attributes
    fixtures = ['test_groups.json', 'test_altitude_datum.json', 'test_counties.json',
                'test_countries.json', 'test_horizontal_datum.json', 'test_nat_aquifer.json',
                'test_states.json', 'test_units.json', 'test_user.json', 'test_agencies.json',
                'test_monitoring_location.json']

    def setUp(self):
        self.usgs_group = Group.objects.get(name='usgs')

        self.add_permission = Permission.objects.get(codename='add_monitoringlocation')
        self.view_permission = Permission.objects.get(codename='view_monitoringlocation')
        self.change_permission = Permission.objects.get(codename='change_monitoringlocation')
        self.delete_permission = Permission.objects.get(codename='delete_monitoringlocation')

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

    def test_site_no_auto_complete_view(self):
        client = Client()
        client.force_login(self.usgs_user)
        resp = client.get('/registry/admin/registry/monitoringlocation/siteno/autocomplete/?term=12345678')
        self.assertIn(b'12345678', resp.content)

    def test_site_no_not_exists_auto_complete_view(self):
        client = Client()
        client.force_login(self.usgs_user)
        resp = client.get('/registry/admin/registry/monitoringlocation/siteno/autocomplete/?term=123456709')
        self.assertIn(b'"results": []', resp.content)
