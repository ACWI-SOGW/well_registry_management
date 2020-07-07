"""
Django Registry Administration.
"""

from django import forms
from django.contrib import admin
from django.db.models.functions import Upper
from django.utils.html import format_html
from .models import CountryLookup, Registry

# this is the Django property for the admin main page header
admin.site.site_header = 'NGWMN Well Registry Administration'
admin.site.login_template = 'registration/login.html'


def check_mark(value):
    """Helper method to create an html formatted entry for the flags in tables."""
    return format_html('&check;') if value == 1 else ''


class RegistryAdminForm(forms.ModelForm):
    """
    Registry admin form.

    This model form is based on fields in models.Registry

    """

    # override the country_cd field
    country_cd = forms.ModelChoiceField(queryset=CountryLookup.objects.all())

    class Meta:
        model = Registry
        fields = '__all__'


def _get_all_groups(user):
    pass


class RegistryAdmin(admin.ModelAdmin):
    """
    Django admin model for the registry application

    """
    form = RegistryAdminForm
    list_display = ('site_id', 'agency_cd', 'site_no', 'displayed', 'has_qw', 'has_wl', 'insert_date', 'update_date')
    list_filter = ('agency_cd', 'site_no', 'update_date')

    # change this value when we have an full UI
    # change_list_template = 'path/to/ui/templates/registry.html

    @staticmethod
    def site_id(obj):
        """Constructs a site id from agency code and site number."""
        return f"{obj.agency_cd}:{obj.site_no}"

    @staticmethod
    def displayed(obj):
        """Transforms display boolean to HTML check mark."""
        return check_mark(obj.display_flag)

    @staticmethod
    def has_qw(obj):
        """Transforms water quality boolean to HTML check mark."""
        return check_mark(obj.qw_sn_flag)

    @staticmethod
    def has_wl(obj):
        """Transforms water level boolean to HTML check mark."""
        return check_mark(obj.wl_sn_flag)

    def _get_groups(self, user):
        """Return a list of upper case groups that this user belongs to"""
        return user.groups.all().values_list(Upper('name'), flat=True)

    def _is_user_in_registry_agency(self, user, registry):
        """Return True if user is a member of the group for registry's agency"""
        return registry.agency_cd in self._get_groups(user)

    def get_readonly_fields(self, request, obj=None):
        return ('agency_cd',) if not request.user.is_superuser else ()

    def get_queryset(self, request):
        return Registry.objects.all() if request.user.is_superuser \
            else Registry.objects.filter(agency_cd__in=self._get_groups(request.user))

    def _has_permission(self, perm, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return request.user.has_perm(perm) \
                   and (not obj or obj.agency_cd in self._get_groups(request.user))

    def has_view_permission(self, request, obj=None):
        return self._has_permission('registry.view_registry', request, obj)

    def has_add_permission(self, request):
        return self._has_permission('registry.add_registry', request)

    def has_change_permission(self, request, obj=None):
        return self._has_permission('registry.change_registry', request)

    def has_delete_permission(self, request, obj=None):
        return self._has_permission('registry.delete_registry', request)

    def get_changeform_initial_data(self, request):
        groups = request.user.groups.all()
        return {
            'agency_cd': '' if request.user.is_superuser or not groups.count() else list(groups)[0].name.upper()
        }

# below here will maintain all the tables Django admin should be aware
admin.site.register(Registry, RegistryAdmin)
