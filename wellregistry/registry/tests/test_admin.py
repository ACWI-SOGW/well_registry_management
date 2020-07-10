"""
Tests for registry admin module
"""
import datetime

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Group
from django.http import HttpRequest
from django.test import TestCase

from ..admin import RegistryAdminForm, RegistryAdmin, check_mark
from ..models import AgencyLookup, CountyLookup, StateLookup, Registry

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

    def test_save_model_new_registry_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.adwr_user
        registry = Registry.objects.create(site_no='11111111')
        self.admin.save_model(request, registry, None, None)

        saved_registry = Registry.objects.get(site_no='11111111')
        self.assertEqual(saved_registry.insert_user, self.adwr_user)
        self.assertEqual(saved_registry.update_user, self.adwr_user)
        self.assertEqual(saved_registry.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

    def test_save_model_new_registry_with_super_user(self):
        request = HttpRequest()
        request.user = self.superuser
        registry = Registry.objects.create(site_no='11111111', agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, registry, None, None)

        saved_registry = Registry.objects.get(site_no='11111111')
        self.assertEqual(saved_registry.insert_user, self.superuser)
        self.assertEqual(saved_registry.update_user, self.superuser)
        self.assertEqual(saved_registry.agency, AgencyLookup.objects.get(agency_cd='ADWR'))

    def test_save_model_existing_registry_with_adwr_user(self):
        request = HttpRequest()
        request.user = self.superuser
        registry = Registry.objects.create(site_no='11111111', agency=AgencyLookup.objects.get(agency_cd='ADWR'))
        self.admin.save_model(request, registry, None, None)

        saved_registry = Registry.objects.get(site_no='11111111')
        saved_registry.site_name = 'A site'
        request.user = self.adwr_user
        self.admin.save_model(request, saved_registry, None, None)
        saved_registry = Registry.objects.get(site_no='11111111')

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
