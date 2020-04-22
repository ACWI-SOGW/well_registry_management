FROM usgswma/python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR $HOME/application

COPY . $HOME/application

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

USER $USER

EXPOSE 8000

CMD ["gunicorn", "--chdir", "wellregistry", "--config", "wellregistry/gunicorn.conf.py", "wellregistry.wsgi"]