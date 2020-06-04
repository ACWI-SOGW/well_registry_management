FROM usgswma/python:3.8

ENV PYTHONUNBUFFERED 1

COPY . $HOME/application

WORKDIR $HOME/application/wellregistry

RUN pip install --no-cache-dir -r ../requirements.txt
RUN pip install --no-cache-dir -r ../requirements-prod.txt

USER $USER

EXPOSE 8000

# Run the Django migrations to ensure the DB tier is up to date.
# Django, like liquibase, executes each entry once.
#
CMD make runmigrations \
 && gunicorn --config wellregistry/gunicorn.conf.py wellregistry.wsgi
