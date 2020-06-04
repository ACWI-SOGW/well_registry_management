"""
# Custom data migration to add groups for each AGENCY defined in AGENCIES
"""
from django.contrib.auth.models import Group, Permission
from django.db import migrations

# Updating the values will cause the migration to be rerun
AGENCIES = [
    u'usgs',
    u'adwr',
    u'mbmg'
]

def apply_migration():
    """
    Add a group for each agency with add, change and delete permissions for the registry table.
    """
    add_p = Permission.objects.get(codename=u'add_registry')
    change_p = Permission.objects.get(codename=u'change_registry')
    delete_p = Permission.objects.get(codename=u'delete_registry')

    existing_agencies = Group.objects.all().values_list('name', flat=True)
    for agency in AGENCIES:
        if agency not in existing_agencies:
            group = Group.objects.create(name=agency)
            group.permissions.set([add_p, change_p, delete_p])
            group.save()


def revert_migration():
    """
    Reverts migration in apply_migration
    """
    Group.objects.filter(name__in=AGENCIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0001_registry_table'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
