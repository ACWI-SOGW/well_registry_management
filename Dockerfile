FROM usgswma/python:3.8

ENV PYTHONUNBUFFERED 1

COPY . $HOME/application
WORKDIR $HOME/application


RUN apt-get update \
 && apt-get install gcc make libpq-dev python3-dev -y \
 && pip install --no-cache-dir -r requirements-prod.txt \
 && pip install --no-cache-dir -r requirements.txt

USER $USER

EXPOSE 8000

CMD gunicorn --chdir wellregistry --config wellregistry/gunicorn.conf.py wellregistry.wsgi
