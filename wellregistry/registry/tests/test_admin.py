"""
Tests for registry admin module
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import TestCase

from ..admin import MonitoringLocationAdmin
from ..models import AgencyLookup, MonitoringLocation


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
