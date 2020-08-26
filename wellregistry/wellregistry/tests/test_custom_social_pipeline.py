"""
Tests for custom_social_pipeline
"""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from ..custom_social_pipeline import change_usgs_user_to_staff, set_superuser_permission

TEST_USERNAME = 'test_user'


class TestChangeUsgsUserToStaff(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(TEST_USERNAME)

    def test_usgs_user(self):
        details = {
            'username': 'testuser@usgs.gov'
        }
        strategy = None
        backend = None
        result = change_usgs_user_to_staff(strategy, details, backend, user=self.user, is_new=True)
        saved_user = get_user_model().objects.get(username=TEST_USERNAME)

        self.assertIs(result.get('user'), self.user)
        self.assertEqual(result.get('is_new'), True)
        self.assertTrue(saved_user.is_staff)
        self.assertEqual(saved_user.groups.filter(name='usgs').count(), 1)

    def test_usgs_contractor_user(self):
        details = {
            'username': 'testuser@contractor.usgs.gov'
        }
        strategy = None
        backend = None
        result = change_usgs_user_to_staff(strategy, details, backend, user=self.user, is_new=True)
        saved_user = get_user_model().objects.get(username=TEST_USERNAME)

        self.assertIs(result.get('user'), self.user)
        self.assertEqual(result.get('is_new'), True)
        self.assertTrue(saved_user.is_staff)
        self.assertEqual(saved_user.groups.filter(name='usgs').count(), 1)

    def test_nonusgs_user(self):
        details = {
            'username': 'testuser@doi.gov'
        }
        strategy = None
        backend = None
        result = change_usgs_user_to_staff(strategy, details, backend, user=self.user, is_new=False)
        saved_user = get_user_model().objects.get(username=TEST_USERNAME)

        self.assertIs(result.get('user'), self.user)
        self.assertEqual(result.get('is_new'), False)
        self.assertFalse(saved_user.is_staff)
        self.assertEqual(saved_user.groups.filter(name='usgs').count(), 0)


class TestSetSuperuserPermission(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(TEST_USERNAME)

    @override_settings(SOCIAL_AUTH_DJANGO_SUPERUSERS=['testuser@usgs.gov'])
    def test_user_superuser(self):
        details = {
            'username': 'testuser@usgs.gov'
        }
        strategy = None
        backend = None
        result = set_superuser_permission(strategy, details, backend, user=self.user, is_new=True)
        saved_user = get_user_model().objects.get(username=TEST_USERNAME)

        self.assertIs(result.get('user'), self.user)
        self.assertEqual(result.get('is_new'), True)
        self.assertTrue(saved_user.is_superuser)

    @override_settings(SOCIAL_AUTH_DJANGO_SUPERUSERS=['testuser@usgs.gov'])
    def test_user_not_superuser(self):
        details = {
            'username': 'testuser@doi.gov'
        }
        strategy = None
        backend = None
        result = set_superuser_permission(strategy, details, backend, user=self.user, is_new=False)
        saved_user = get_user_model().objects.get(username=TEST_USERNAME)

        self.assertIs(result.get('user'), self.user)
        self.assertEqual(result.get('is_new'), False)
        self.assertFalse(saved_user.is_superuser)
