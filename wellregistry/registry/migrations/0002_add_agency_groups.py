"""
# Custom data migration to add groups for each AGENCY defined in AGENCIES
"""
from django.db import migrations

#pylint: disable=unused-argument

# Updating the values will cause the migration to be rerun
AGENCIES = [
    u'usgs',
    u'adwr',
    u'mbmg'
]

def apply_migration(apps, schema_editor):
    """
    Add a group for each agency with add, change and delete permissions for the registry table.
    """
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Registry = apps.get_model('registry', 'Registry')
    content_type = ContentType.objects.get_for_model(Registry)

    # Create permissions if the post migrate signal has not been issued after Registry table creation
    add_p, created = Permission.objects.get_or_create(codename=u'add_registry', content_type=content_type)
    change_p, created = Permission.objects.get_or_create(codename=u'change_registry', content_type=content_type)
    delete_p, created = Permission.objects.get_or_create(codename=u'delete_registry', content_type=content_type)

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

    dependencies = [
        ('registry', '0001_registry_table'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
