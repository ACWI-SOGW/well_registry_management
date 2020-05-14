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
from wellregistry.settings import DATABASE_USERNAME
from wellregistry.settings import APP_DATABASE_NAME
from wellregistry.settings import APP_DB_OWNER_USERNAME
from wellregistry.settings import APP_DB_OWNER_PASSWORD
from wellregistry.settings import APP_SCHEMA_OWNER_USERNAME
from wellregistry.settings import APP_SCHEMA_OWNER_PASSWORD
import registry.pgsql_utils as pgsql


class Migration(migrations.Migration):
    """
    SQL to create the database and user roles.

    This creates a new database and schema owner in PG for an application specific name.
    The "postgres" database and password is Already created during database install.

    instance (daemon)
        postgres database
            'postgres' admin user name and password
                loosely like the Oracle 'sys' schema
        application database
        app db owner(roles)
            a postgres role granted logon and DDL
            with optional schemas, 'public' default
        read-only user(roles)
            (typical but not the registry)
            a postgres role granted logon and SELECT only access
        client user(roles)
            (aka agency or provider) connection to postgres for all django client actions
            a postgres role granted logon and SELECT access and CRUD/DML on limited tables
            all client logins will be authenticated with login.gov
        admin user(roles)
            (aka superuser) connection to postgres for all django admin actions
            a postgres role granted logon and all CRUD/DML access
            first authenticated with login.gov
                then authenticated with django admin login
    """

    initial = False

    dependencies = [('registry', '0000_create_database')]

    if 'test' in sys.argv:
        operations = []
    else:
        operations = [

            # create a login user that will own the application database
            migrations.RunSQL(
                sql=pgsql.create_login_role(APP_DB_OWNER_USERNAME, APP_DB_OWNER_PASSWORD),
                reverse_sql=pgsql.drop_role(APP_DB_OWNER_USERNAME)),

            migrations.RunSQL(
                sql=f"GRANT ALL PRIVILEGES ON DATABASE {APP_DATABASE_NAME} TO {APP_DB_OWNER_USERNAME};",
                reverse_sql=f"REVOKE ALL PRIVILEGES ON DATABASE {APP_DATABASE_NAME} FROM {APP_DB_OWNER_USERNAME};"),

            # rolls can be granted to others, here the postgres superuser is granted the app db owner roll
            migrations.RunSQL(
                sql=pgsql.grant_role(APP_DB_OWNER_USERNAME, DATABASE_USERNAME),
                reverse_sql=pgsql.revoke_role(APP_DB_OWNER_USERNAME, DATABASE_USERNAME)),

            # assign the application database owner
            migrations.RunSQL(
                sql=f"ALTER DATABASE {APP_DATABASE_NAME} OWNER TO {APP_DB_OWNER_USERNAME};",
                reverse_sql=f"ALTER DATABASE {APP_DATABASE_NAME} OWNER TO {DATABASE_USERNAME};"),

            # create a login user that will own the application schema
            migrations.RunSQL(
                sql=pgsql.create_login_role(APP_SCHEMA_OWNER_USERNAME, APP_SCHEMA_OWNER_PASSWORD),
                reverse_sql=pgsql.drop_role(APP_SCHEMA_OWNER_USERNAME)),

            # the postgres superuser is granted the app db owner roll
            migrations.RunSQL(
                sql=pgsql.grant_role(APP_SCHEMA_OWNER_USERNAME, APP_DB_OWNER_USERNAME),
                reverse_sql=pgsql.revoke_role(APP_SCHEMA_OWNER_USERNAME, APP_DB_OWNER_USERNAME)),

            # create a database specific to the application
            # this is how we would like to do it if Django connections were compatible.
            # see 0000_create_database.py for proxy migration workaround.
            # migrations.RunSQL(
            #     sql=f"CREATE DATABASE {APP_DATABASE_NAME} WITH OWNER = {APP_DB_OWNER_USERNAME};",
            #     reverse_sql=f"DROP DATABASE IF EXISTS {APP_DB_OWNER_USERNAME};"),
        ]
