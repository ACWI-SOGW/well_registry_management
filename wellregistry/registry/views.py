"""
Registry application views.

"""
from django.http import JsonResponse
from django.views.generic.base import TemplateView


class BasePage(TemplateView):
    """
    Landing page.

    """
    template_name = 'base.html'


def status_check(request):
    """
    JSON response for health checks.

    """
    resp = {'status': 'up'}
    return JsonResponse(resp)
