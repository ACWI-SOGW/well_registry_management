from django.views.generic.base import TemplateView

# Create your views here.


class BasePage(TemplateView):

    template_name = 'base.html'
