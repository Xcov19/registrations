import asyncio

import fastapi
import uvloop

from registrations.infrastructure.adapters.api.routers import register_hospital

app = fastapi.FastAPI(
    title="XCoV19 Registrations service.",
    debug=True,
    description="""Hospital Registrations that
    registers healthcare data points, user registration.
    """,
)
app.include_router(register_hospital.router)

uvloop.install()

if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    # TODO: fill up config.toml
    # config.from_toml("config.toml")
    config.bind = "0.0.0.0:8080"
    asyncio.run(serve(app, config))
