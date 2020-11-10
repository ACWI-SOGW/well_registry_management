"""
Custom auto complete view
"""

from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.http import JsonResponse


class SiteNoAutoCompleteView(AutocompleteJsonView):
    """Handle Siteno autocomplete request."""
    term = ''
    object_list = None

    def get(self, request, *args, **kwargs):
        self.term = request.GET.get('term', '')
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {'text': obj['site_no'], 'id': obj['site_no']}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })

    def get_queryset(self):
        """Return queryset based on ModelAdmin.get_site_no_search_results()."""

        qs = self.model_admin.get_queryset(self.request)
        qs, search_use_distinct = self.model_admin.get_site_no_search_results(self.request, qs, self.term)
        if search_use_distinct:
            qs = qs.distinct()
        return qs
