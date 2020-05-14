"""
After the registry table is created,
this will grant access to th client login
"""
from django.db import migrations
from wellregistry.settings import APP_SCHEMA_NAME
from wellregistry.settings import APP_CLIENT_USERNAME


class Migration(migrations.Migration):
    """
    Django Migration.

    SQL to grant the client access to the registry table.

    """
    initial = False

    dependencies = [('registry', '0002_initial')]

    operations = [
        # grant CRUD to app user -- after 0001_initial, this cannot be granted until the tables is created
        migrations.RunSQL(
            sql=f"""
                GRANT INSERT, SELECT, UPDATE, DELETE
                ON {APP_SCHEMA_NAME}.registry
                TO {APP_CLIENT_USERNAME}
            """,
            reverse_sql=f"""
                REVOKE INSERT, SELECT, UPDATE, DELETE
                ON {APP_SCHEMA_NAME}.registry
                FROM {APP_CLIENT_USERNAME}
            """),
    ]
