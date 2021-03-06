# healthcare registrations

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

Microservice that allows CCCs (covid health care centers) to register themselves via a web form.
This service provides an unverified dump of registered hospitals.

Based on hexagonal architecture design on fastapi designed to run as a microservice.

## How to Run

#### TL;DR:
Do
```bash
docker compose up --build
```

and hit : `http://0.0.0.0:8081/docs`
to check the openspec api docs.

### Prerequisites
You need to install docker machine & docker compose.

### Docker Compose

```bash
docker-compose up --build
```

### On Gitpod

```bash
https://gitpod.io/#https://github.com/Xcov19/registrations
```

### Developing
Make sure to install `pyenv` locally and do:
```bash
sudo apt install -y python3-testresources sqlite3 libsqlite3-dev
sudo apt install sqlite3

PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions --enable-optimizations" LDFLAGS="-L/usr/local/opt/sqlite/lib" CPPFLAGS="-I/usr/local/opt/sqlite/include" pyenv install 3.9.7
```

and then setup your poetry package in a separate virtual environment.
For instance, this is the poetry package install in Ubuntu:
1. Setup poetry like:```python3 -m pip install --user --no-cache-dir poetry```
2. Create a `pyenv virtualenv 3.9.7 <YOUR VENV NAME>`
3. `pyenv activate <YOUR VENV NAME>`
4. Set your venv and install packages like:
```bash
poetry env use /home/<YOUR USERNAME>/.pyenv/versions/<PY_VERSION>/bin/python3 && poetry install
```
In this case the `PY_VERSION` is `3.9.7`
You would need to do something similar in your OS platform specific environment.
Refer to poetry documentation.

If you are locally developing & debugging you could do:
```bash
poetry run hypercorn -k uvloop --bind="0.0.0.0:8080" --debug --reload registrations.infrastructure.adapters.api.app:app
```

Then hit:
`http://0.0.0.0:8080/docs`

to view the existing openAPI docs.

To run tests, do:
```bash
poetry run pytest -m fast tests
```

#### A note on Type Annotations

Have a read on effective type hints with mypy for motivation behind building a type annotated codebase:
https://blog.wolt.com/engineering/2021/09/30/professional-grade-mypy-configuration/

### Pending Todos:
- [x] dockerize
- [ ] postgresql plug
- [ ] nosql plug
- [ ] add project to supabase.io
- [ ] [add support for alembic auto schema versioning](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [ ] upgrade docker file with shell scripts that run alembic migrations and run fastapi hypercorn server.
- [ ] [expose protobuf grpc api for other services to consume registered hospital data](https://github.com/grpc-ecosystem/grpc-cloud-run-example/blob/master/python/README.md). [Read grpc literature here](https://grpc.io/docs/what-is-grpc/core-concepts/#rpc-life-cycle)
- [ ] deploy to google cloud run
