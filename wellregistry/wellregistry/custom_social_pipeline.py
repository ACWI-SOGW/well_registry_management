'''
Custom social pipeline functions
'''

from django.contrib.auth.models import Group
from django.conf import settings

# pylint: disable=unused-argument

def change_usgs_user_to_staff(strategy, details, backend, *args, user=None, **kwargs):
    """
    Social auth pipeline function to change usgs users automatically to have is_staff set and
    to add the usgs permissions to the user.
    :return: dict
    """
    if kwargs.get('is_new'):
        email = details.get('username')
        if '@usgs.gov' in email or '@contractor.usgs.gov' in email:
            user.is_staff = True
            user.save()
            usgs_group = Group.objects.get(name='usgs')
            usgs_group.user_set.add(user)
    return {
        'is_new': kwargs.get('is_new'),
        'user': user
    }


def set_superuser_permission(strategy, details, backend, *args, user=None, **kwargs):
    """
    Social auth piplien function to set user to superuser if username is in SOCIAL_AUTH_DJANGO_SUPERUSERS
    :return: dict
    """
    email = details.get('username')
    if email in settings.SOCIAL_AUTH_DJANGO_SUPERUSERS:
        user.is_superuser = True
        user.save()
    return {
        'is_new': kwargs.get('is_new'),
        'user': user
    }
