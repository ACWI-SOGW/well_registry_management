# The below suppresses pylint message: Module name "0002_add_agency_groups" doesn't conform to snake_case naming style
# pylint: disable-msg=C0103
# Enable check for the rest of the file
# pylint: enable-msg=C0103
"""
# Custom data migration to add groups for each AGENCY defined in AGENCIES
"""
from django.db import migrations

#pylint: disable=unused-argument
#pylint: disable=invalid-name

# Updating the values will cause the migration to be rerun
AGENCIES = [
    'usgs',
    'adwr',
    'mbmg'
]

def apply_migration(apps, schema_editor):
    """
    Add a group for each agency with add, change and delete permissions for the registry table.
    """

    #pylint: disable=unused-variable
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Registry = apps.get_model('registry', 'Registry')
    content_type = ContentType.objects.get_for_model(Registry)

    # Create permissions if the post migrate signal has not been issued after Registry table creation
    add_p, created = Permission.objects.get_or_create(codename='add_registry', content_type=content_type)
    change_p, created = Permission.objects.get_or_create(codename='change_registry', content_type=content_type)
    delete_p, created = Permission.objects.get_or_create(codename='delete_registry', content_type=content_type)

    existing_agencies = Group.objects.all().values_list('name', flat=True)
    for agency in AGENCIES:
        if agency not in existing_agencies:
            group = Group.objects.create(name=agency)
            group.permissions.set([add_p, change_p, delete_p])
            group.save()


def revert_migration(apps, schema_editor):
    """
    Reverts migration in apply_migration
    """
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=AGENCIES).delete()


class Migration(migrations.Migration):
    """
    Adds a group for each agency and gives permissions for add/change/delete_registry.
    """

    dependencies = [
        ('registry', '0001_registry_table'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
