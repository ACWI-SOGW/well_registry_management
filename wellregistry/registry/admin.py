"""
Django Registry Administration.
"""

from django import forms
from django.contrib import admin
from django.db.models.functions import Upper
from .models import MonitoringLocation, AgencyLookup

# this is the Django property for the admin main page header
admin.site.site_header = 'NGWMN Well Registry Administration'
admin.site.login_template = 'registration/login.html'


class MonitoringLocationAdminForm(forms.ModelForm):
    """
    Registry admin form.
    """
    class Meta:
        model = MonitoringLocation
        widgets = {
            'wl_well_purpose_notes': forms.Textarea(),
            'qw_well_purpose_notes': forms.Textarea(),
            'link': forms.Textarea()
        }
        fields = '__all__'


def _get_groups(user):
    """Return a list of upper case groups that this user belongs to"""
    return user.groups.all().values_list(Upper('name'), flat=True)


def _has_permission(perm, user, obj=None):
    """Return true if the user has permission, perm, for the obj"""
    if user.is_superuser:
        return True

    return user.has_perm(perm) and (not obj or obj.agency.agency_cd in _get_groups(user))

class SelectListFilter(admin.RelatedFieldListFilter):
    """
    Django admin select list filter to implement a picker for the filter.
    """
    template = "admin/choice_list_filter.html"

class MonitoringLocationAdmin(admin.ModelAdmin):
    """
    Django admin model for the registry application
    """
    form = MonitoringLocationAdminForm
    list_display = ('site_id', 'agency', 'site_no', 'display_flag', 'wl_sn_flag', 'qw_sn_flag',
                    'insert_date', 'update_date')
    list_filter = (('agency', SelectListFilter), 'site_no', 'update_date')

    @staticmethod
    def site_id(obj):
        """Constructs a site id from agency code and site number."""
        # The obj field agency_cd is the AgencyLovLookup model, retrieve agency_cd from the model
        return f"{obj.agency.agency_cd}:{obj.site_no}"

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
        return MonitoringLocation.objects.all() if request.user.is_superuser \
            else MonitoringLocation.objects.filter(agency__in=_get_groups(request.user))

    def has_view_permission(self, request, obj=None):
        """Overrides default implementation"""
        return _has_permission('registry.view_registry', request.user, obj)

    def has_add_permission(self, request):
        """Overrides default implementation"""
        return _has_permission('registry.add_registry', request.user)

    def has_change_permission(self, request, obj=None):
        """Overrides default implementation"""
        return _has_permission('registry.change_registry', request.user, obj)

    def has_delete_permission(self, request, obj=None):
        """Overrides default implementation"""
        return _has_permission('registry.delete_registry', request.user, obj)


# below here will maintain all the tables Django admin should be aware
admin.site.site_url = None
admin.site.enable_nav_sidebar = False
admin.site.register(MonitoringLocation, MonitoringLocationAdmin)
