"""
Register Django URL route names.
"""
from django.urls import path

from .views import BasePage, status_check


urlpatterns = [
    path('', BasePage.as_view(), name='base'),
    path('status', status_check, name='status')
]
