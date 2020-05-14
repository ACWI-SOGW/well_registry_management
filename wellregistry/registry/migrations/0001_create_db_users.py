"""
Migrate initial users and roles.
https://docs.djangoproject.com/en/3.0/topics/migrations/

This one migration should be run on the 'postgres' database alias.
> python manage.py migrate --database=postgres  registry 0000
All subsequent migrations should be run on the 'migration'
> python manage.py migrate --database=migration

"""
from django.db import migrations
from wellregistry.settings import DATABASE_USERNAME
from wellregistry.settings import APP_DATABASE_NAME
from wellregistry.settings import APP_DB_OWNER_USERNAME
from wellregistry.settings import APP_DB_OWNER_PASSWORD
from wellregistry.settings import APP_SCHEMA_NAME
from wellregistry.settings import APP_SCHEMA_OWNER_USERNAME
from wellregistry.settings import APP_SCHEMA_OWNER_PASSWORD
from wellregistry.settings import APP_ADMIN_USERNAME
from wellregistry.settings import APP_ADMIN_PASSWORD
from wellregistry.settings import APP_CLIENT_USERNAME
from wellregistry.settings import APP_CLIENT_PASSWORD


def create_login_role(username, password):
    """Helper method to construct SQL: create role."""
    # "create role if not exists" is not valid syntax
    return f"DROP ROLE IF EXISTS {username}; CREATE ROLE {username} WITH LOGIN PASSWORD '{password}';"


def drop_role(role):
    """Helper method to construct SQL: drop role."""
    return f"DROP ROLE IF EXISTS {role};"


def grant_role(role, target):
    """Helper method to construct SQL: grant privilege."""
    return f"GRANT {role} to {target};"


def revoke_role(role, target):
    """Helper method to construct SQL: revoke privilege."""
    return f"REVOKE {role} from {target};"


def grant_default(schema, defaults, target):
    if defaults is 'CRUD':
        defaults = "INSERT, SELECT, UPDATE, DELETE"

    return f"""
        ALTER DEFAULT PRIVILEGES 
        IN SCHEMA {schema} 
        GRANT {defaults} 
        ON TABLES TO {target};
    """


def revoke_default(schema, defaults, target):
    if defaults is 'CRUD':
        defaults = "INSERT, SELECT, UPDATE, DELETE"

    return f"""
        ALTER DEFAULT PRIVILEGES 
        IN SCHEMA {schema} 
        REVOKE {defaults} 
        ON TABLES FROM {target}
    """


def alter_search_path():
    return f"""
        ALTER DATABASE {APP_DATABASE_NAME}
        SET search_path = {APP_ADMIN_USERNAME}, {APP_SCHEMA_NAME}, public;
    """


def reset_search_path():
    return f"""
        ALTER DATABASE {APP_DATABASE_NAME}
        SET search_path = {APP_ADMIN_USERNAME}, {APP_SCHEMA_NAME}, public;
    """


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

    operations = [
        # create a login user that will own the application database
        migrations.RunSQL(
            sql=create_login_role(APP_DB_OWNER_USERNAME, APP_DB_OWNER_PASSWORD),
            reverse_sql=drop_role(APP_DB_OWNER_USERNAME)),

        # rolls can be granted to others, here the postgres superuser is granted the app db owner roll
        migrations.RunSQL(
            sql=grant_role(APP_DB_OWNER_USERNAME, DATABASE_USERNAME),
            reverse_sql=revoke_role(APP_DB_OWNER_USERNAME, DATABASE_USERNAME)),

        # assign the application database owner
        migrations.RunSQL(
            sql=f"ALTER DATABASE {APP_DATABASE_NAME} OWNER TO {APP_DB_OWNER_USERNAME};",
            reverse_sql=f"ALTER DATABASE {APP_DATABASE_NAME} OWNER TO {DATABASE_USERNAME};"),

        # create a login user that will own the application schema
        migrations.RunSQL(
            sql=create_login_role(APP_SCHEMA_OWNER_USERNAME, APP_SCHEMA_OWNER_PASSWORD),
            reverse_sql=drop_role(APP_SCHEMA_OWNER_USERNAME)),

        # the postgres superuser is granted the app db owner roll
        migrations.RunSQL(
            sql=grant_role(APP_SCHEMA_OWNER_USERNAME, APP_DB_OWNER_USERNAME),
            reverse_sql=revoke_role(APP_SCHEMA_OWNER_USERNAME, APP_DB_OWNER_USERNAME)),

        # create a database specific to the application
        # this is how we would like to do it if Django connections were compatible.
        # see 0000_create_database.py for proxy migration workaround.
        # migrations.RunSQL(
        #     sql=f"CREATE DATABASE {APP_DATABASE_NAME} WITH OWNER = {APP_DB_OWNER_USERNAME};",
        #     reverse_sql=f"DROP DATABASE IF EXISTS {APP_DB_OWNER_USERNAME};"),

        # create a application specific schema
        migrations.RunSQL(
            sql=f"CREATE SCHEMA IF NOT EXISTS {APP_SCHEMA_NAME}",
            reverse_sql=None if (APP_SCHEMA_NAME is 'public')
                else f"DROP SCHEMA IF EXISTS {APP_SCHEMA_NAME};"),

        migrations.RunSQL(
            sql=f"ALTER DATABASE {APP_DATABASE_NAME} SET search_path = {APP_SCHEMA_NAME}, public;",
            reverse_sql=f"ALTER DATABASE {APP_DATABASE_NAME} RESET search_path;"),

        # create a login user that will used by the Django admin process to manage entries
        migrations.RunSQL(
            sql=create_login_role(APP_ADMIN_USERNAME, APP_ADMIN_PASSWORD),
            reverse_sql=drop_role(APP_ADMIN_USERNAME)),

        # grant CRUD to admin user
        migrations.RunSQL(
            sql=grant_default(APP_SCHEMA_NAME, 'CRUD', APP_ADMIN_USERNAME),
            reverse_sql=revoke_default(APP_SCHEMA_NAME, 'CRUD', APP_ADMIN_USERNAME)),
        
        # create a login user that will used by the app users to manage entries
        migrations.RunSQL(
            sql=create_login_role(APP_CLIENT_USERNAME, APP_CLIENT_PASSWORD),
            reverse_sql=drop_role(APP_CLIENT_USERNAME)),

        # grant select to client user
        migrations.RunSQL(
            sql=grant_default(APP_SCHEMA_NAME, 'SELECT', APP_CLIENT_USERNAME),
            reverse_sql=revoke_default(APP_SCHEMA_NAME, 'SELECT', APP_CLIENT_USERNAME)),

        # grant CRUD to app user -- after 0001_initial, this cannot be granted until the tables is created
    ]
