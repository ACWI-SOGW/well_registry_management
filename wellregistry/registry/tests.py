"""
Tests for the registry application
"""

from django.test import RequestFactory, TestCase
from .admin import RegistryAdmin, check_mark
from .models import Registry
from .views import BasePage, status_check


class TestBasePage(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_base_page(self):
        req = self.factory.get('/registry')
        resp = BasePage.as_view()(req)
        self.assertEqual(resp.status_code, 200)


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


class TestRegistryAdmin(TestCase):

    def test_site_id(self):
        # SETUP
        reg_entry = Registry()
        reg_entry.agency_cd = 'provider'
        reg_entry.site_no = '12345'
        reg = RegistryAdmin(model=reg_entry, admin_site=None)

        # TEST ACTION
        site_id = reg.site_id(reg_entry)

        # ASSERTION
        self.assertEqual(site_id, "provider:12345")

    def test_check_mark(self):
        # SETUP
        true_flag = True
        false_flag = False

        # TEST ACTION
        check_html = check_mark(true_flag)
        blank_html = check_mark(false_flag)

        # ASSERTION
        self.assertEqual(check_html, '&check;')
        self.assertEqual(blank_html, '')
