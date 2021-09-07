"""
Django Registry Administration.
"""
from django.contrib import admin

from ..models import MonitoringLocation, CountyLookup
from .monitoring_location import MonitoringLocationAdmin, CountyLookupAdmin

admin.site.site_header = 'NGWMN Monitoring Locations Registry Administration'
admin.site.login_template = 'registration/login.html'
admin.site.site_url = None
admin.site.enable_nav_sidebar = False
admin.site.register(MonitoringLocation, MonitoringLocationAdmin)
admin.site.register(CountyLookup, CountyLookupAdmin)
