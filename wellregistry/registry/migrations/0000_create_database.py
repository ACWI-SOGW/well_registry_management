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
from django.conf import settings as env
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Migration(migrations.Migration):
    """
    Proxy migration for creating the application database.

    Django connections cannot 'create database' because of transactions.
    the method will create its own connection to create the database.

    """

    initial = True

    dependencies = []

    operations = []

    def __init__(self, type1=None, type2=None):
        """For this proxy, call the create database custom SQL."""
        super().__init__(type1, type2)
        create_database()


def create_database():
    """
    Creates the application database.

    This creates its own connection because Django connections
    cannot execute postgres 'create database'

    Notice that it runs two SQL commands.
    The first checks the database existence.
    While the second creates the database if it is needed.

    """
    if 'test' not in sys.argv:
        with psycopg2.connect(database=env.DATABASE_NAME, user=env.DATABASE_USERNAME, password=env.DATABASE_PASSWORD,
                              host=env.DATABASE_HOST, port=env.DATABASE_PORT) as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            sql_database_not_exists = f"""
                SELECT 1 as needed
                WHERE NOT EXISTS 
                (SELECT FROM pg_database 
                WHERE datname = '{env.APP_DATABASE_NAME}');
            """
            sql_create_db = f"CREATE DATABASE {env.APP_DATABASE_NAME};"

            cursor.execute(sql_database_not_exists)
            rows = cursor.fetchall()

            if rows:
                print(f"'{env.APP_DATABASE_NAME}' database exists!")
            else:
                print(f"'{env.APP_DATABASE_NAME}' database needed.")

            for row in rows:
                if row[0] == 1:
                    cursor.execute(sql_create_db)
                    print(f"'{env.APP_DATABASE_NAME}' database created.")
