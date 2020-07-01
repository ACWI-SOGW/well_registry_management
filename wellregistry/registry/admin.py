"""
Django Registry Administration.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Registry

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
        # The obj field agency_cd is the AgencyLovLookup model, retrieve agency_cd from the model
        return f"{obj.agency_cd.agency_cd}:{obj.site_no}"

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


# below here will maintain all the tables Django admin should be aware
admin.site.register(Registry, RegistryAdmin)
