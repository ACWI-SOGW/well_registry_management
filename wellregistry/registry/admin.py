"""
Django Registry Administration.
"""

from django import forms
from django.contrib import admin
from django.db.models.functions import Upper
from django.utils.html import format_html
from .models import Registry, AgencyLookup

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
    class Meta:
        model = Registry
        fields = '__all__'


def _get_groups(user):
    """Return a list of upper case groups that this user belongs to"""
    return user.groups.all().values_list(Upper('name'), flat=True)


class RegistryAdmin(admin.ModelAdmin):
    """
    Django admin model for the registry application

    """
    form = RegistryAdminForm
    list_display = ('site_id', 'agency', 'site_no', 'displayed', 'has_qw', 'has_wl', 'insert_date', 'update_date')
    list_filter = ('agency', 'site_no', 'update_date')

    # change this value when we have an full UI
    # change_list_template = 'path/to/ui/templates/registry.html

    @staticmethod
    def site_id(obj):
        """Constructs a site id from agency code and site number."""
        # The obj field agency_cd is the AgencyLovLookup model, retrieve agency_cd from the model
        return f"{obj.agency.agency_cd}:{obj.site_no}"

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

    @staticmethod
    def _get_groups(user):
        """Return a list of upper case groups that this user belongs to"""
        return user.groups.all().values_list(Upper('name'), flat=True)

    @staticmethod
    def _is_user_in_registry_agency(user, registry):
        """Return True if user is a member of the group for registry's agency"""
        return registry.agency.agency_cd in _get_groups(user)

    @staticmethod
    def _has_permission(perm, user, obj=None):
        """Return true if the user has permission, perm, for the obj"""
        if user.is_superuser:
            return True
        else:
            return user.has_perm(perm) \
                   and (not obj or obj.agency.agency_cd in _get_groups(user))

    def save_model(self, request, obj, form, change):
        if not obj.insert_user:
            obj.insert_user = request.user
        obj.update_user = request.user

        if not obj.agency and not request.user.is_superuser:
            obj.agency = AgencyLookup.objects.get(agency_cd=_get_groups(request.user)[0])

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Overrides default implementation"""
        return ('agency',) if not request.user.is_superuser else ()

    def get_queryset(self, request):
        """Overrides default implementation"""
        return Registry.objects.all() if request.user.is_superuser \
            else Registry.objects.filter(agency__in=_get_groups(request.user))

    def has_view_permission(self, request, obj=None):
        """Overrides default implementation"""
        return self._has_permission('registry.view_registry', request.user, obj)

    def has_add_permission(self, request):
        """Overrides default implementation"""
        return self._has_permission('registry.add_registry', request.user)

    def has_change_permission(self, request, obj=None):
        """Overrides default implementation"""
        return self._has_permission('registry.change_registry', request.user, obj)

    def has_delete_permission(self, request, obj=None):
        """Overrides default implementation"""
        return self._has_permission('registry.delete_registry', request.user, obj)


# below here will maintain all the tables Django admin should be aware
admin.site.register(Registry, RegistryAdmin)
