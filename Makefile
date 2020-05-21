PYTHON := env/bin/python
PIP := env/bin/pip

.PHONY: cleanenv devenv prodenv test watch

cleanenv:
	@echo 'Cleaning environment....'
	rm -rf env/

watch:
	$(PYTHON) wellregistry/manage.py runserver

devenv: env common-env-requirements local-dev-requirements wellregistry/.env

prodenv: env common-env-requirements prod-requirements wellregistry/.env

test:
	$(PYTHON) wellregistry/manage.py test

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