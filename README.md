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
2. Create a `pyenv virtualenv 3.9.7 .venv`;
3. `pyenv activate .venv`; Unfortunately, for now we need to lock the name to `.venv`
4. Set your venv and install packages configuration in a file `poetry.toml` like:
    ```bash
    # set virtualenvs
    [virtualenvs]
    create = true
    in-project = true
    path = ".venv"
    ```
5. Install packages like:
    ```bash
    poetry install -vvv
    ```

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

### Structure of core project

Structurally the core project is more or less hexagonal architecture.
It has layers represented below from a top to bottom view,
the top layer being interfaces that the application interacts with outside world to
the inner logic which has no context of dependent moving parts and are plain language objects.

#### I/O Adapters
Depends on: Application services, Infrastructure services.

#### Application services:
Consumes: IO
Depends on: Unit of Work, DTO, Domain services.

#### Domain services:
Consumes: Interfaces, Parameters.
Depends on: Unit of Work, Aggregates.

#### Unit of Work
Consumes: Domain service.
Depends on: Repositories.

#### Repositories:
Consumes: UOW.
Depends on: Aggregate, DTO.

```bash
registrations/
├── domain
│   ├── dto.py  # keeps data transfer objects between IO<->Application services and Domain Entities<->Database Schema
│   ├── hospital  # domain logic
│   │   ├── __init__.py
│   │   └── registration.py
│   ├── __init__.py
│   ├── location  # domain logic
│   │   ├── __init__.py
│   │   └── location.py
│   ├── repo  # Repository interface to interact with database implementation and domain entity.
│   │   ├── __init__.py
│   │   └── registration_repo.py
│   └── services  # domain and application services
│       ├── application_services.py
│       ├── hospital_registration_services.py
│       └── __init__.py
├── infrastructure
│   ├── adapters  # IO implementation of interfaces defined in core application domain.
│   │   ├── api
│   │   ├── __init__.py
│   │   └── repos  # Repository implementation to interact with storage.
│   ├── __init__.py
│   └── services  # infrastructure services
│       └── __init__.py
└── __init__.py

```

### Pending Todos:
- [x] dockerize
- [x] postgresql plug (m3o); [See here](https://github.com/Xcov19/registrations/pull/30#issue-1340536435)
- [ ] Add cron job for Gdata API pull from gsheets
- [ ] Enrich the Api to save more healthcare metadata
- [ ] ~~nosql plug~~
- [ ] ~~add project to supabase.io~~
- [ ] ~~[add support for alembic auto schema versioning](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)~~
- [ ] ~~upgrade docker file with shell scripts that run alembic migrations and run fastapi hypercorn server.~~
- [ ] [expose protobuf grpc api for other services to consume registered hospital data](https://github.com/grpc-ecosystem/grpc-cloud-run-example/blob/master/python/README.md). [Read grpc literature here](https://grpc.io/docs/what-is-grpc/core-concepts/#rpc-life-cycle)
- [x] deploy to google cloud run
