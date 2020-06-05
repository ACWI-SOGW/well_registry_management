"""
Tests for registry admin module
"""
from django.test import TestCase

from ..admin import RegistryAdmin, check_mark
from ..models import Registry


class TestRegistryAdmin(TestCase):

    def test_site_id(self):
        # SETUP
        reg_entry = Registry()
        reg_entry.agency_cd = 'provider'
        reg_entry.site_no = '12345'

        # TEST ACTION
        site_id = RegistryAdmin.site_id(reg_entry)

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
