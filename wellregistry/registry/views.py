"""
Registry application views.
"""
from django.http import JsonResponse
from django.views.generic.base import TemplateView

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

class MonitoringLocationsListView(ListAPIView):
    serializer_class = RegistrySerializer

    def get_queryset(self):
        """
        Override to take query parameter display to filter results
        """
        queryset = Registry.objects.all()
        if "display" in self.request.GET:
            queryset = queryset.filter(display_flag__iexact=self.request.GET.get('display'))

        return queryset
