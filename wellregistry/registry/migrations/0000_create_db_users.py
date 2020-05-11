"""
    migration: initial users and roles
"""
from django.db import migrations
from wellregistry.wellregistry.env import Environment


def create_login_role(username, password):
    """helper method to construct SQL: create role"""
    return f"CREATE ROLE {username} WITH LOGIN PASSWORD '{password}';"


def drop_role(role):
    """helper method to construct SQL: drop role"""
    return f"DROP ROLE IF EXISTS {role};"


def grant_role(role, target):
    """helper method to construct SQL: grant privilege"""
    return f"GRANT {role} to {target};"


def revoke_role(role, target):
    """helper method to construct SQL: revoke privilege"""
    return f"REVOKE {role} from {target};"


class Migration(migrations.Migration):
    """Django Migration:
    This creates a new database and schema owner in PG for an application specific name.
    The "postgres" database and password is Already created during database install.
    """

    initial = True

    dependencies = []

    env = Environment()

    operations = [
        # create a login user that will own the application database
        migrations.RunSQL(
            sql=create_login_role(env.APP_DB_OWNER_USERNAME, env.APP_DB_OWNER_PASSWORD),
            reverse_sql=drop_role(env.APP_DB_OWNER_USERNAME)),

        # rolls can be granted to others, here the postgres superuser is granted the app db owner roll
        migrations.RunSQL(
            sql=grant_role(env.APP_DB_OWNER_USERNAME, env.DATABASE_USERNAME),
            reverse_sql=revoke_role(env.APP_DB_OWNER_USERNAME, env.DATABASE_USERNAME)),

        # create a login user that will own the application schema
        migrations.RunSQL(
            sql=create_login_role(env.APP_SCHEMA_OWNER_USERNAME, env.APP_SCHEMA_OWNER_PASSWORD),
            reverse_sql=drop_role(env.APP_DB_OWNER_USERNAME)),

        # the postgres superuser is granted the app db owner roll
        migrations.RunSQL(
            sql=grant_role(env.APP_SCHEMA_OWNER_USERNAME, env.APP_DB_OWNER_USERNAME),
            reverse_sql=revoke_role(env.APP_SCHEMA_OWNER_USERNAME, env.APP_DB_OWNER_USERNAME)),

        # create a database specific to the application
        migrations.RunSQL(
            sql=f"CREATE DATABASE {env.APP_DATABASE_NAME} WITH OWNER = {env.APP_DB_OWNER_USERNAME};",
            reverse_sql=f"DROP DATABASE IF EXISTS {env.APP_DB_OWNER_USERNAME};"),

        # create a login user that will used by the Django admin process to manage entries
        migrations.RunSQL(
            sql=create_login_role(env.APP_ADMIN_USERNAME, env.APP_ADMIN_PASSWORD),
            reverse_sql=drop_role(env.APP_ADMIN_USERNAME)),

        # create a application specific schema
        migrations.RunSQL(
            sql=f"CREATE SCHEMA {env.APP_SCHEMA}",
            reverse_sql=f"DROP SCHEMA IF EXISTS {env.APP_SCHEMA};"),

        # grant CRUD to admin user
        migrations.RunSQL(
            sql=f"""
                ALTER DEFAULT PRIVILEGES 
                IN SCHEMA {env.APP_SCHEMA} 
                GRANT INSERT, SELECT, UPDATE, DELETE 
                ON TABLES TO {env.APP_ADMIN_USERNAME}
            """,
            reverse_sql=f"""
                ALTER DEFAULT PRIVILEGES 
                IN SCHEMA {env.APP_SCHEMA} 
                REVOKE INSERT, SELECT, UPDATE, DELETE 
                ON TABLES FROM {env.APP_ADMIN_USERNAME}
            """),

        # create a login user that will used by the app users to manage entries
        migrations.RunSQL(
            sql=create_login_role(env.APP_CLIENT_USERNAME, env.APP_CLIENT_PASSWORD),
            reverse_sql=drop_role(env.APP_CLIENT_USERNAME)),

        # grant CRUD to app user -- after 0001_initial, this cannot be granted until the tables is created
    ]
