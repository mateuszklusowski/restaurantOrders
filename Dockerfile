FROM python:3.10.4-slim-buster
LABEL maintainer="klusowskimat@gmail.com"

ENV PYTHONUNBUFFERED=1

COPY /requirements.txt /tmp/requirements.txt
COPY /requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && apt-get -y install libpq-dev gcc && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser --disabled-password --no-create-home project-user

ENV PATH="/py/bin:$PATH"

USER project-user
