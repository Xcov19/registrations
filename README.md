# healthcare registrations

Microservice that allows CCCs (covid health care centers) to register themselves via a web form.

pending Todos:
- [x] dockerize
- [ ] nosql plug

Based on clean architecture design on fastapi designed to run as a microservice.

## How to Run

### Prerequisites
You need to install docker machine & docker compose.

### Docker Compose

```bash
docker-compose up --build
```

### Developing
If you are locally developing & debugging you could do:
```bash
python3 main.py
```

Then hit:
`http://0.0.0.0:8080/docs`
