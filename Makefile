PYTHON := env/bin/python
PIP := env/bin/pip

.PHONY: cleanenv devenv prodenv test watch runmigrations runlint

.IGNORE: runlint

cleanenv:
	@echo 'Cleaning environment....'
	rm -rf env/

watch:
	$(PYTHON) wellregistry/manage.py runserver

devenv: env common-env-requirements local-dev-requirements wellregistry/.env

prodenv: env common-env-requirements prod-requirements wellregistry/.env

test:
	cd wellregistry && ../$(PYTHON) manage.py test

runmigrations:
	env/bin/python wellregistry/manage.py migrate --database=postgres postgres
	#env/bin/python wellregistry/manage.py migrate registry 0000
	env/bin/python wellregistry/manage.py migrate admin
	env/bin/python wellregistry/manage.py migrate auth
	env/bin/python wellregistry/manage.py migrate contenttypes
	env/bin/python wellregistry/manage.py migrate sessions
	env/bin/python wellregistry/manage.py migrate social_django
	env/bin/python wellregistry/manage.py migrate registry 0001_registry_table
	env/bin/python wellregistry/manage.py migrate registry 0002_add_agency_groups

runlint:
	env/bin/pylint wellregistry/postgres
	env/bin/pylint wellregistry/registry
	env/bin/pylint wellregistry/wellregistry/
	env/bin/pylint ./**/*.py

env:
	@echo 'Creating local environment....'
	virtualenv --python=python3.8 --no-download env

common-env-requirements:
	$(PIP) install -r requirements.txt

wellregistry/.env:
	@echo 'Creating environment variables file'
	cp wellregistry/.env.sample wellregistry/.env

local-dev-requirements:
	$(PIP) install -r requirements-dev.txt

prod-requirements:
	$(PIP) install -r requirements-prod.txt