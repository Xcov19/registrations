from typing import Callable

import fastapi
from fastapi import Depends

import repo
from models import HealthCareData
from repo import MongoRepo
from use_case import HospitalRegistrationUseCase
from use_case import register_use_case

router = fastapi.APIRouter(on_startup=[repo.start_psql_client])
register_hospital_use_case = register_use_case(
    HospitalRegistrationUseCase, repo.PsqlRepo
)


# TODO: add dependency injection using Depends, refactor use_cases
@router.post(
    "/register-center",
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def register_hospital_center(
    healthcare_data: HealthCareData,
):
    if not register_hospital_use_case.valid_new_entry(healthcare_data):
        return fastapi.exceptions.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Not a valid entry."
        )
    if not register_hospital_use_case.duplicate_exists(healthcare_data):
        return fastapi.exceptions.HTTPException(
            fastapi.status.HTTP_409_CONFLICT, detail="Entry already exists."
        )
    return register_hospital_use_case.create_entry(healthcare_data)
