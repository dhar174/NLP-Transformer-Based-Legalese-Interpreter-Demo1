# syntax=docker/dockerfile:1
FROM python:3.6-slim-buster
WORKDIR /app

COPY . .
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install https://blackstone-model.s3-eu-west-1.amazonaws.com/en_blackstone_proto-0.0.1.tar.gz



EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
RUN export FLASK_APP=app && \
    export FLASK_ENV=development

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port", "5000"]