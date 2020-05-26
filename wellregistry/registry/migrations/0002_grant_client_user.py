"""
After the registry table is created,this will grant access to th client login
"""
import sys

from django.db import migrations
from django.conf import settings

env = settings.ENVIRONMENT


class Migration(migrations.Migration):
    """
    Django Migration.

    SQL to grant the client access to the registry table.

    """
    initial = False

    dependencies = [('registry', '0001_registry_table')]

    if 'test' in sys.argv:
        operations = []
    else:
        operations = [
            # grant CRUD to app user -- after 0001_initial, this cannot be granted until the tables is created
            migrations.RunSQL(
                sql=f"""
                    GRANT INSERT, SELECT, UPDATE, DELETE
                    ON {env['APP_SCHEMA_NAME']}.registry_registry
                    TO {env['APP_CLIENT_USERNAME']}
                """,
                reverse_sql=f"""
                    REVOKE INSERT, SELECT, UPDATE, DELETE
                    ON {env['APP_SCHEMA_NAME']}.registry_registry
                    FROM {env['APP_CLIENT_USERNAME']}
                """),
        ]
