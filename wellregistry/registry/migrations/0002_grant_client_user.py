"""
After the registry table is created,
this will grant access to th client login
"""
from django.db import migrations
from wellregistry.wellregistry.env import Environment


class Migration(migrations.Migration):
    """Django Migration: grant registry access to client login."""

    initial = False

    dependencies = [('migrations', '0001_initial')]

    env = Environment()

    operations = [
        # grant CRUD to app user -- after 0001_initial, this cannot be granted until the tables is created
        migrations.RunSQL(
            sql=f"""
                GRANT INSERT, SELECT, UPDATE, DELETE
                ON {env.APP_SCHEMA}.registry
                TO {env.APP_CLIENT_USERNAME}
            """,
            reverse_sql=f"""
                REVOKE INSERT, SELECT, UPDATE, DELETE
                ON {env.APP_SCHEMA}.registry
                FROM {env.APP_CLIENT_USERNAME}
            """),
    ]
