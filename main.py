import fastapi
from starlette import status

import settings
from entities import HealthCareData, NewHealthCareData
from repo import MongoRepo
from use_case import HospitalRegistrationUseCase

app = fastapi.FastAPI(
    debug=settings.DEBUG,
)

register_hospital_use_case = HospitalRegistrationUseCase(MongoRepo)


@app.post(
    "/register-center",
    status_code=status.HTTP_201_CREATED,
    response_model=NewHealthCareData,
)
async def register_hospital_center(
    healthcare_data: HealthCareData,
) -> NewHealthCareData:
    if not register_hospital_use_case.valid_new_entry(healthcare_data):
        fastapi.exceptions.HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Not a valid entry."
        )
    if not register_hospital_use_case.duplicate_exists(healthcare_data):
        fastapi.exceptions.HTTPException(
            status.HTTP_409_CONFLICT, detail="Entry already exists."
        )
    return await register_hospital_use_case.create_entry(healthcare_data)


if __name__ == "__main__":
    from hypercorn import run as hypercorn_run
    from hypercorn.config import Config

    config = Config()
    # TODO: fill up config.toml
    config.from_toml("config.toml")
    hypercorn_run.run(config)
