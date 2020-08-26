"""
Register Django URL route names.
"""
from django.urls import path

from .views import BasePage, MonitoringLocationsListView, status_check


urlpatterns = [
    path('', BasePage.as_view(), name='home'),
    path('monitoring-locations/', MonitoringLocationsListView.as_view(), name="api-monitoring-locations"),
    path('status/', status_check, name='status')
]
