import asyncio

import fastapi
import uvloop
from starlette import status

import settings
from models import HealthCareData
from repo import MongoRepo
from use_case import HospitalRegistrationUseCase

app = fastapi.FastAPI(
    debug=settings.DEBUG,
)


register_hospital_use_case = HospitalRegistrationUseCase(MongoRepo)

uvloop.install()

# TODO: add dependency injection using Depends, refactor use_cases
@app.post(
    "/register-center",
    status_code=status.HTTP_201_CREATED,
)
async def register_hospital_center(
    healthcare_data: HealthCareData,
):
    if not register_hospital_use_case.valid_new_entry(healthcare_data):
        return fastapi.exceptions.HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Not a valid entry."
        )
    if not register_hospital_use_case.duplicate_exists(healthcare_data):
        return fastapi.exceptions.HTTPException(
            status.HTTP_409_CONFLICT, detail="Entry already exists."
        )
    await register_hospital_use_case.create_entry(healthcare_data)


if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = "0.0.0.0:8080"
    # TODO: fill up config.toml
    # config.from_toml("config.toml")
    asyncio.run(serve(app, config))
