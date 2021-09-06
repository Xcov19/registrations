FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY requirements.txt /requirements.txt

RUN python3 -m pip install -U pip && pip install --no-cache-dir -r /requirements.txt

RUN rm -rf *

WORKDIR /app

COPY . /app

# ENTRYPOINT hypercorn -k uvloop --insecure-bind="172.17.0.1:8080" --debug --reload main
