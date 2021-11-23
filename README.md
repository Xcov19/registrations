# healthcare registrations

Microservice that allows CCCs (covid health care centers) to register themselves via a web form.
This service provides an unverified dump of registered hospitals.

Based on clean architecture design on fastapi designed to run as a microservice.

## How to Run

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
If you are locally developing & debugging you could do:
```bash
python3 main.py
```

Then hit:
`http://0.0.0.0:8080/docs`

### Pending Todos:
- [x] dockerize
- [ ] postgresql plug
- [ ] nosql plug
- [ ] add project to supabase.io
- [ ] [add support for alembic auto schema versioning](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [ ] upgrade docker file with shell scripts that run alembic migrations and run fastapi hypercorn server.
- [ ] [expose protobuf grpc api for other services to consume registered hospital data](https://github.com/grpc-ecosystem/grpc-cloud-run-example/blob/master/python/README.md). [Read grpc literature here](https://grpc.io/docs/what-is-grpc/core-concepts/#rpc-life-cycle)
- [ ] deploy to google cloud run
