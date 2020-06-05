FROM usgswma/python:3.8

ENV PYTHONUNBUFFERED 1

COPY . $HOME/application

WORKDIR $HOME/application/wellregistry

RUN apt-get update \
 && apt-get install gcc libpq-dev python3-dev -y \
 && pip install --no-cache-dir -r ../requirements-prod.txt \
 && apt-get autoremove --purge -y gcc libpq-dev python3-dev \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir -r ../requirements.txt

USER $USER

EXPOSE 8000

# Run the Django migrations to ensure the DB tier is up to date.
# Django, like liquibase, executes each entry once.
#
CMD gunicorn --config wellregistry/gunicorn.conf.py wellregistry.wsgi
