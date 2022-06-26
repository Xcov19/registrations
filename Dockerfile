FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim-2021-10-02
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /requirements.txt

# See:
RUN apt-get update -y
#RUN add-apt-repository universe && apt-get update -y && apt install -y python3-testresources
RUN apt install -y libsqlite3-dev
RUN python3 -m pip install -U pip && python3 -m pip install --no-cache-dir poetry

RUN rm -rf *

WORKDIR /app

COPY *.py /app
COPY LICENSE /app
COPY README.md /app
COPY settings.json /app
COPY storage /app
COPY *.toml /app
COPY poetry.lock /app

RUN poetry install -vvv
