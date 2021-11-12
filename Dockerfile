FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /requirements.txt

RUN python3 -m pip install -U pip && pip install --no-cache-dir -r /requirements.txt

RUN rm -rf *

WORKDIR /app

COPY . /app
