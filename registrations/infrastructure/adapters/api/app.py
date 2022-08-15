#!/usr/bin/env python3
import asyncio
import os.path

import fastapi
import phonenumbers
import uvloop
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from registrations.infrastructure.adapters.api.routers import (
    register_hospital_router,
)
from registrations.utils.errors import InvalidRegistrationEntryError

LOCAL_PORT = os.getenv("LOCAL_PORT")


def build_cors_flight(app: fastapi.FastAPI) -> fastapi.FastAPI:
    documentation_api = os.getenv("DOCUMENTATION_API")
    allow_origins = [
        f"0.0.0.0:{LOCAL_PORT}",
        f"http://localhost:{LOCAL_PORT}",
        f"https://localhost:{LOCAL_PORT}",
        documentation_api,
    ]
    allow_methods = [
        "GET",
        "POST",
    ]
    allow_headers = [
        "Content-Type",
        "Authorization",
        "Accept",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )
    return app


app = fastapi.FastAPI(
    title="XCoV19 Registrations service.",
    debug=True,
    description="""Hospital Registrations that
    registers healthcare data points, user registration.
    """,
)
app.include_router(register_hospital_router.router)
app = build_cors_flight(app)


@app.exception_handler(InvalidRegistrationEntryError)
async def invalid_entry_exception_handler(
    _request: Request,
    exc: InvalidRegistrationEntryError,
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=400,
        content={"message": f"{exc}"},
    )


@app.exception_handler(phonenumbers.phonenumberutil.NumberParseException)
async def invalid_phone_number_exception_handler(
    _request: Request,
    exc: phonenumbers.phonenumberutil.NumberParseException,
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": f"{exc}"},
    )


uvloop.install()

if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"0.0.0.0:{LOCAL_PORT}"]
    config_toml_file = os.path.join(os.path.dirname(__file__), "config.toml")
    if os.path.exists(config_toml_file):
        config.from_toml("config.toml")
    asyncio.run(serve(app, config))  # type: ignore[arg-type]
