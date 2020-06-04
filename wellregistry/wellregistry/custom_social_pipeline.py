'''
Custom social pipeline functions
'''

from django.contrib.auth.models import Group
from django.conf import settings

def change_usgs_user_to_staff(strategy, details, backend, user=None, *args, **kwargs):
    if kwargs.get('is_new'):
        email = details.get('username')
        if email.find('@usgs.gov') != -1:
            user.is_staff = True
            user.save()
            usgs_group = Group.objects.get(name=u'usgs')
            usgs_group.user_set.add(user)
    return {
        'is_new': kwargs.get('is_new'),
        'user': user
    }

def set_superuser_permission(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('username')
    if email in settings.SOCIAL_AUTH_DJANGO_SUPERUSERS:
        user.is_superuser = True
        user.save()
    return {
        'is_new': kwargs.get('is_new'),
        'user': user
    }