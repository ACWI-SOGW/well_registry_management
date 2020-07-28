FROM usgswma/python:3.8

ENV PYTHONUNBUFFERED 1

COPY . $HOME/application

# Install npm to be used to install application dependencies
RUN apt-get update \
	&& apt-get install -y curl gnupg \
	&& curl --silent --location https://deb.nodesource.com/setup_12.x | bash - \
	&& apt-get install -y nodejs

WORKDIR $HOME/application/wellregistry
RUN npm install

WORKDIR $HOME/application
RUN apt-get update \
 && apt-get install gcc libpq-dev python3-dev -y \
 && pip install --no-cache-dir -r requirements-prod.txt \
 && pip install --no-cache-dir -r requirements.txt

RUN python wellregistry/manage.py collectstatic --clear --no-input

USER $USER

EXPOSE 8000

CMD gunicorn --chdir wellregistry --config wellregistry/gunicorn.conf.py wellregistry.wsgi
