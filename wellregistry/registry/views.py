"""
Registry application views.
"""
from django.http import JsonResponse
from django.views.generic.base import TemplateView

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.generics import ListAPIView

from .models import MonitoringLocation
from .serializers import MonitoringLocationSerializer


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
    REST API for monitoring location registry
    """
    serializer_class = MonitoringLocationSerializer
    queryset = MonitoringLocation.objects.all().select_related('agency', 'country', 'state', 'county',
                                                               'horizontal_datum', 'altitude_units',
                                                               'altitude_datum', 'well_depth_units',
                                                               'nat_aqfr', 'insert_user', 'update_user')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['display_flag']
