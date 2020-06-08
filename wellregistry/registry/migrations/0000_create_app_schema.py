"""
Migrate initial users and roles.
https://docs.djangoproject.com/en/3.0/topics/migrations/
This one migration should be run on the 'postgres' database alias.
> python manage.py migrate --database=postgres  registry 0000
All subsequent migrations should be run on the 'migration'
> python manage.py migrate --database=migration
"""
import sys

from django.db import migrations
from django.conf import settings
import wellregistry.pgsql_utils as pgsql

env = settings.ENVIRONMENT


class Migration(migrations.Migration):
    """

    """

    initial = False

    dependencies = []
    # We have an option here. we can use the empty dependencies or the following 'postgres' migration dependency.
    # dependencies = [('postgres', '0001_create_db_users')]
    # However, when a dependency is used then the executions must be in he django_migrations table.
    # In order for this metadata to be correct in the application database requires that the migration
    # for postgres entries to be run in fake mode for the application database. This prevents them from
    # running twice and causing errors. In an attempt to make them idempotent, the roles are dropped first.
    # It turns out that if the roles have dependencies then they cannot be dropped. This drop was done
    # because there is no CREATE ROLE IF NOT EXISTS in postgres. Also, there is no clean way for Django to
    # check if an object exists like we have for the yaml based liquibase changelogs.
    # python -m manage migrate --fake postgres

    if 'test' in sys.argv:
        operations = []
    else:
        operations = [

            # create a application specific schema within the database the connection is made
            migrations.RunSQL(
                sql=f"""CREATE SCHEMA IF NOT EXISTS {env['APP_SCHEMA_NAME']}
                        AUTHORIZATION {env['APP_SCHEMA_OWNER_USERNAME']};""",
                reverse_sql=f"DROP SCHEMA IF EXISTS {env['APP_SCHEMA_NAME']};"),

            migrations.RunSQL(
                sql=f"ALTER DATABASE {env['APP_DATABASE_NAME']} SET search_path = {env['APP_SCHEMA_NAME']}, public;",
                reverse_sql=f"ALTER DATABASE {env['APP_DATABASE_NAME']} RESET search_path;"),

        ]