"""
Tests for custom template tags
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from ..templatetags.group_filters import is_in_group


class TestIsInGroup(TestCase):
    fixtures = ['test_groups.json', 'test_user.json']

    def setUp(self):
        self.adwr_group = Group.objects.get(name='adwr')
        self.usgs_group = Group.objects.get(name='usgs')

        self.adwr_user = get_user_model().objects.create_user('adwruser')
        self.adwr_user.groups.add(self.adwr_group)
        self.adwr_user.is_staff = True
        self.adwr_user.save()

        self.usgs_user = get_user_model().objects.create_user('usgsuser')
        self.usgs_user.groups.add(self.usgs_group)
        self.usgs_user.is_staff = True
        self.usgs_user.save()

    def test_user_in_group(self):
        self.assertTrue(is_in_group(self.usgs_user, 'usgs'))
        self.assertTrue(is_in_group(self.adwr_user, 'adwr'))

    def test_user_not_in_group(self):
        self.assertFalse(is_in_group(self.usgs_user, 'adwr'))
        self.assertFalse(is_in_group(self.adwr_user, 'usgs'))
