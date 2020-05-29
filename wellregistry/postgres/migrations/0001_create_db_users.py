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
    SQL to create the database admin roles.

    This creates a database owner and a schema owner in PG for an application specific name.
    The "postgres" database and password is already created during database install.
    """
    initial = False

    dependencies = [('postgres', '0000_create_database')]

    if 'test' in sys.argv:
        operations = []
    else:
        operations = [

            # create a login user that will own the application database
            migrations.RunSQL(
                sql=pgsql.create_login_role(env['APP_DB_OWNER_USERNAME'], env['APP_DB_OWNER_PASSWORD']),
                reverse_sql=pgsql.drop_role(env['APP_DB_OWNER_USERNAME'])),

            migrations.RunSQL(
                sql=f"GRANT ALL PRIVILEGES ON DATABASE {env['APP_DATABASE_NAME']} TO {env['APP_DB_OWNER_USERNAME']};",
                reverse_sql=f"""REVOKE ALL PRIVILEGES ON DATABASE {env['APP_DATABASE_NAME']}
                                FROM {env['APP_DB_OWNER_USERNAME']};"""),

            # roles can be granted to others, here the postgres superuser is granted the app db owner role
            migrations.RunSQL(
                sql=pgsql.grant_role(env['APP_DB_OWNER_USERNAME'], env['DATABASE_USERNAME']),
                reverse_sql=pgsql.revoke_role(env['APP_DB_OWNER_USERNAME'], env['DATABASE_USERNAME'])),

            # assign the application database owner
            migrations.RunSQL(
                sql=f"ALTER DATABASE {env['APP_DATABASE_NAME']} OWNER TO {env['APP_DB_OWNER_USERNAME']};",
                reverse_sql=f"ALTER DATABASE {env['APP_DATABASE_NAME']} OWNER TO {env['DATABASE_USERNAME']};"),

            # create a user that will own the application schema
            migrations.RunSQL(
                sql=pgsql.create_login_role(env['APP_SCHEMA_OWNER_USERNAME'], env['APP_SCHEMA_OWNER_PASSWORD']),
                reverse_sql=pgsql.drop_role(env['APP_SCHEMA_OWNER_USERNAME'])),

            # the postgres superuser is granted the app schema owner role
            migrations.RunSQL(
                sql=pgsql.grant_role(env['APP_SCHEMA_OWNER_USERNAME'], env['APP_DB_OWNER_USERNAME']),
                reverse_sql=pgsql.revoke_role(env['APP_SCHEMA_OWNER_USERNAME'], env['APP_DB_OWNER_USERNAME'])),
        ]
