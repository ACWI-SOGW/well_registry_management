from django.contrib import admin
from django.utils.html import format_html
from .models import Registry

# this is the Django property for the admin main page header
admin.site.site_header = 'NGWMN Well Registry Administration'


def check_mark(value):
    """
    This is a helper method to create an html formatted entry for the flags in tables.
    """
    return format_html('&check;') if value == 1 else ''


class MultiDBModelAdmin(admin.ModelAdmin):
    """
    This is a Django example from
    https://docs.djangoproject.com/en/3.0/topics/db/multi-db/#s-exposing-multiple-databases-in-django-s-admin-interface
    It controls the connection used by admin actions. When a database action passes through this instance
    it selects the database 'using' for the admin connection. It is best practice that admin actions are on
    a separate connection than standard users.
    All model admin should have an handler the extends this class.
    When using more than the 'default' database alias then it is required to set the 'using' value to the database alias
    to use in a db action. This helper class ensures that the admin access to the registry table uses the connection
    alias with the appropriate granted access or db roles.
    see RegistryAdmin for an example.
    """
    # A handy constant for the name of the alternate connection.
    using = 'admin_connection'

    def save_model(self, request, obj, form, change):
        """
        Tell Django to save objects to the 'other' database.
        """
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        """
        Tell Django to delete objects from the 'other' database
        """
        obj.delete(using=self.using)

    def get_queryset(self, request):
        """
        Tell Django to look for objects on the 'other' database.
        """
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Tell Django to populate ForeignKey widgets using a query on the 'other' database.
        """
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Tell Django to populate ManyToMany widgets using a query on the 'other' database.
        """
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


class RegistryAdmin(MultiDBModelAdmin):
    """Django Registry Manager
    Model class that manages how to display a Registry object in the Django admin.
    It extends MultiDBModelAdmin so that it utilizes the admin database connection.
    see MultiDBModelAdmin
    """
    list_display = ('site_id', 'agency_cd', 'site_no', 'displayed', 'has_qw', 'has_wl', 'insert_date', 'update_date',)
    list_filter = ('agency_cd', 'site_no', 'update_date',)

    # change this value when we have an full UI
    # change_list_template = 'path/to/ui/templates/registry.html

    def site_id(self, obj):
        """
        constructs a site id from agency code and site number
        """
        return f"{obj.agency_cd}:{obj.site_no}"

    def displayed(self, obj):
        """
        transforms display boolean to HTML check mark
        """
        return check_mark(obj.display_flag)

    def has_qw(self, obj):
        """
        transforms water quality boolean to HTML check mark
        """
        return check_mark(obj.qw_sn_flag)

    def has_wl(self, obj):
        """
        transforms water level boolean to HTML check mark
        """
        return check_mark(obj.wl_sn_flag)


# below here will maintain all the tables Django admin should be aware
admin.site.register(Registry, RegistryAdmin)
