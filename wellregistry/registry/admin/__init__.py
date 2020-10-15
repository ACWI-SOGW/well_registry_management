"""
Django Registry Administration.
"""
from django.contrib import admin

from .monitoring_location import MonitoringLocationAdmin
from ..models import MonitoringLocation, CountyLookup, StateLookup, CountryLookup

admin.site.site_header = 'NGWMN Well Registry Administration'
admin.site.login_template = 'registration/login.html'
admin.site.site_url = None
admin.site.enable_nav_sidebar = False
admin.site.register(MonitoringLocation, MonitoringLocationAdmin)
