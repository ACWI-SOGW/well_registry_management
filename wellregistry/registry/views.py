from django.http import JsonResponse
from django.views.generic.base import TemplateView


class BasePage(TemplateView):

    template_name = 'base.html'


def status_check(request):
    resp = {'status': 'up'}
    return JsonResponse(resp)
