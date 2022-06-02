# syntax=docker/dockerfile:1
FROM python:3.6-buster
WORKDIR /app

LABEL maintainer="darf333@gmail.com"

ENV LISTEN_PORT 5000

EXPOSE 5000


COPY . /app
WORKDIR /app

RUN pip3 install --force-reinstall -r requirements.txt
RUN pip3 install https://blackstone-model.s3-eu-west-1.amazonaws.com/en_blackstone_proto-0.0.1.tar.gz




ENV FLASK_APP=app.py
ENV FLASK_ENV=development
RUN export FLASK_APP=app && \
    export FLASK_ENV=development

CMD [ "gunicorn", "--conf", "/app/gunicorn_conf.py", "--bind", "0.0.0.0:5000", "app:app"]