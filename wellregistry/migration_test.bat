@echo off

REM This is a sample script to set env and run migration.
REM With the migrations all in one Django app, it was required to
REM run a --fake run but now that it is separate apps this is no
REM long necessary. However, the 0000 script in the registry app
REM executes a database search_path update that is not taking effect
REM on the current connection. If the 0000 script is run in isolation
REM then subsequent connections inherit the proper search_path.

SET DEBUG=True

SET DATABASE_USERNAME=postgres
SET DATABASE_PASSWORD=qwerty
SET DATABASE_HOST=localhost
SET DATABASE_PORT=5432

SET APP_DATABASE_NAME=well_registry
SET APP_DB_OWNER_USERNAME=registry
SET APP_DB_OWNER_PASSWORD=qwerty_1

SET APP_SCHEMA_NAME=well_registry_schema
SET APP_SCHEMA_OWNER_USERNAME=schema_owner
SET APP_SCHEMA_OWNER_PASSWORD=testing

SET APP_ADMIN_USERNAME=django_admin
SET APP_ADMIN_PASSWORD=qwerty_2
SET APP_CLIENT_USERNAME=django_user
SET APP_CLIENT_PASSWORD=qwerty_3

rem python -m manage migrate --fake postgres
python -m manage migrate registry
python -m manage migrate admin
python -m manage migrate auth
python -m manage migrate contenttypes
python -m manage migrate sessions
python -m manage migrate social_django
python -m manage runserver
