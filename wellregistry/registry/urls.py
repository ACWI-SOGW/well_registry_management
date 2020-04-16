from django.urls import path

from .views import BasePage


urlpatterns = [
    path('', BasePage.as_view(), name='base')
]
