from django.contrib import admin
from django.utils.html import format_html
from .models import Registry

admin.site.site_header = 'NGWMN Well Registry Administration'


def check_mark(value):
    return format_html('&check;') if value == 1 else ''


class RegistryAdmin(admin.ModelAdmin):
    list_display = ('site_id', 'agency_cd', 'site_no', 'displayed', 'has_qw', 'has_wl', 'insert_date', 'update_date',)
    list_filter = ('agency_cd', 'site_no', 'update_date',)

    # change this value when we have an full UI
    # change_list_template = 'path/to/ui/templates/registry.html

    def site_id(self, obj):
        return "%s:%s" % (obj.agency_cd, obj.site_no)

    def displayed(self, obj):
        return check_mark(obj.display_flag)

    def has_qw(self, obj):
        return check_mark(obj.qw_sn_flag)

    def has_wl(self, obj):
        return check_mark(obj.wl_sn_flag)


admin.site.register(Registry, RegistryAdmin)
