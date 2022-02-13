FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /requirements.txt

# See: https://gist.github.com/y56/0540d22a1db40dacc7fbbb93c866821e
RUN apt install -y python3-testresources libsqlite3-dev
RUN python3 -m pip install -U pip && python3 -m pip install --no-cache-dir poetry \
    && poetry install

RUN rm -rf *


WORKDIR /app

COPY . /app
