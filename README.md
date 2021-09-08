# Monitoring Location Registry Management System

[![Build Status](https://travis-ci.org/ACWI-SOGW/well_registry_management.svg?branch=master)](https://travis-ci.org/ACWI-SOGW/well_registry_management)
[![codecov](https://codecov.io/gh/ACWI-SOGW/well_registry_management/branch/master/graph/badge.svg)](https://codecov.io/gh/ACWI-SOGW/well_registry_management)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6af41d5963ee48c1bb9f8a83ea338b46)](https://www.codacy.com/gh/ACWI-SOGW/well_registry_management?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ACWI-SOGW/well_registry_management&amp;utm_campaign=Badge_Grade)

Application for management of groundwater monitoring locations.

## Development Server
Once the project has been cloned, the user should ensure a clean environment. This can be
done with 
```bash
make cleanenv
```
### Installing requirements
The user can then install the requirements. Both scripts will create an initial .env file that
assumes that a local postgres database is available. See below for instructions on using a docker container
to run a local postgres database. Installing the postgres module psycopg2 can be
challenging on some environments so two options are provided. The first
```bash
make devenv
```
installs psycopg2-binary. This should never be done in for deployment or in the docker container. Instead use
```bash
make prodenv
```
This installs psycopg2 module which has some environment prerequisites. See <https://www.psycopg.org/docs/install.html> for details

### Tests and Linting
The tests require a postgres database. The docker ci database can be used to run these tests. Start the docker ci database and ensure the application's DATABASE_HOST is set to localhost before running the tests. See [Using Docker ci database.](#using-docker-ci-database)
To run tests locally:
```bash
make test
```

You can also easily run pylint against all python modules using:
```bash
make runlint
```

### Running migrations
The Django environment requires a database. On an empty database, you will need to run the migrations. Care 
should be taken to ensure that you are running migrations against the local database. It is not harmful to run the migrations again as previously run migrations will be skipped.

```bash
make runmigrations
``` 

There is also a sample batch script to configure a local postgres instance on Windows.
```bash 
    migration_test.bat
```

If running by hand please note that the order of migrations should be maintained.

Notice that the first scripts are run while connecting for the only time with the postgres user. Subsequent migrations run while connected to the application database. The 0000 migration must be run on its own because it sets the search_path to use the application schema. Subsequent connections default to placing new objects (DDL) in the application schema properly.

### Running local development server
The Django local development can be run as follows:
```bash
make watch
```
Another means to run local is the manage.py from within the wellregistry path:
```bash
env/bin/python wellregistry/manage.py runserver
```

Use `localhost` instead of `127.0.0.1` for local development, otherwise a KeyCloak bug
regarding an invalid `redirect_uri` will be encountered when authenticating.

## Running in a docker container locally
To build the container:
```bash
docker build ./ -t well_registry_app
```

To run the container:
```bash
docker run --env-file wellregistry/.env -p 8000:8000 well_registry_app
```

If you are running the docker ci database locally, your .env file DATABASE_HOST will need to change in order for the application within a docker container can talk to another container. On Macs, you can set DATABASE_HOST to host.docker.internal 

## Using Docker ci database
The docker ci database can be started with the start_ci_db.bash script. Keep in mind that any existing instance will be removed first.
To manually start, run the following command:
```bash
docker pull usgswma/well-registry-db:ci
docker run --name registry_postgres -d -p 5432:5432 usgswma/well-registry-db:ci
```

You can stop the container using:
```bash
docker stop registry_postgres
```
You can start the container again:
```bash
docker start registry_postgres
```

## Environment Variables

Environment variables are used to configure this application. In order to facilitate local development
the developer can create a .env file with the necessary environment variables. There is a sample
file at ./wellregistry/.env.sample which will be copied to ./env if the make devenv or make prodenv
command is executed and no .env file already exists. Below is the description of the variables.
All variables are described in <https://docs.djangoproject.com/en/3.0/ref/settings> unless noted.

### General
```bash
DEBUG: boolean - true for debug level logging
``` 

### Django Deployment 
These environment variables are required for the tier deployment. They are not used for local development.
```bash
SECRET_KEY: Django cryptographic signing key
ALLOWED_HOSTS: list of host domain names for this application to respond
CIDR_RANGES: list of IP ranges allowed used in django-allow-cidr. Is used to
        set ALLOWED_CIDR_NETS which is defined in allow_cidr.middleware.AllowCIDRMiddleware
```

### Database (root)
The DATABASE values are defined to connect to cloud RDS or local DB installation.These values are used by the initial Django migrations *only* to configure the application.
```bash
DATABASE_NAME: posgres database name
DATABASE_HOST: posgres host url 
    - use 'localhost' for local development database
    - use the actual tier database host URL for cloud deployment
DATABASE_PORT: optional posgres port - if not specified then default is '5432' 
DATABASE_USERNAME: postgres root user name
DATABASE_PASSWORD: postgres root password
```

### Database (app)
The following should be set to initial values for a new database configuration.When setting up the database to run the initial migration scripts the values are flexible. They are arbitrarily configurable for local database development. However, once the database has been configured they are not arbitrary and must be the values used to configure that database. For example, if the application database is new the it could be called 'well_registry' or 'ngwmn_registry' but once the scripts have run to create that database, the values must remain unchanged. Continuing the example, if 'well_registry' is used for the database name then it must remain 'well_registry' in order for the application to use it. The point is that these values are used for configuration and runtime after configuration. Some addition example values are given below. 

The application database ensures that application data is not stored in the postgres system database. It also enables multiple application to share a database instance.
```bash
APP_DATABASE_NAME:     name for the applicaiton database within postgres
APP_DB_OWNER_USERNAME: user name for the database owner
APP_DB_OWNER_PASSWORD: database owner password
```
The application schema ensure that application data is not stored in the default public schema. The configuration assigns this schema as the primary search_path.
```bash
APP_SCHEMA_NAME:           name for the application schema
APP_SCHEMA_OWNER_USERNAME: owner user name for the application schema
APP_SCHEMA_OWNER_PASSWORD: schema owner password
```
This connection will allow maintenance of all registry entries in support of user issues. It has less restricted table CRUD roles than the application user.
 ```bash
APP_ADMIN_USERNAME: user name for the connection used by the registry administration
APP_ADMIN_PASSWORD: administration login password
```
This connection is the standard or default application user connection. It has limited table CRUD roles.
```bash
APP_CLIENT_USERNAME: user name for the connection used by the registry users
APP_CLIENT_PASSWORD: user level login password
```