from django.contrib import admin
from django.utils.html import format_html
from .models import Registry

admin.site.site_header = 'NGWMN Well Registry Administration'


def check_mark(value):
    return format_html('&check;') if value == 1 else ''


class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate connection.
    using = 'admin_connection'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


class RegistryAdmin(MultiDBModelAdmin):
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
