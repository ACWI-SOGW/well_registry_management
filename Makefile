PYTHON := env/bin/python
PIP := env/bin/pip


clean:
	@echo 'Cleaning environment....'
	rm -rf env/

watch:
	$(PYTHON) wellregistry/manage.py runserver

env:
	@echo 'Creating local environment....'
	virtualenv --python=python3.6 --no-download env
	$(PIP) install -r requirements.txt