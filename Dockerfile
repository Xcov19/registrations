FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim-2021-10-02
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt install -y libsqlite3-dev
RUN python3 -m pip install -U pip && python3 -m pip install --no-cache-dir poetry

WORKDIR /app

ADD registrations /app/registrations
COPY LICENSE /app
COPY *.toml /app
COPY poetry.lock /app

ENV PYTHONPATH /app
RUN export PYTHONPATH=$PYTHONPATH:/app/registrations/
RUN poetry install -vvv
