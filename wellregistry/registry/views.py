"""
Registry application views.
"""
from django.http import JsonResponse
from django.views.generic.base import TemplateView

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import ListAPIView

from .models import Registry
from .serializers import RegistrySerializer


class BasePage(TemplateView):
    """
    Landing page.

    """
    template_name = 'registry/index.html'


def status_check(request):
    """
    JSON response for health checks.

    """
    # because the argument is framework we will ignore
    # pylint: disable=unused-argument
    resp = {'status': 'up'}
    return JsonResponse(resp)


class MonitoringLocationsListView(ListAPIView):  # pylint: disable=too-few-public-methods
    """
    REST API for monitoring locations
    """
    serializer_class = RegistrySerializer
    queryset = Registry.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['display_flag']
