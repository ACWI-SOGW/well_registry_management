"""
Tests for the registry  views module
"""
from django.test import RequestFactory, TestCase

from ..views import BasePage, status_check


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
