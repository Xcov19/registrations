import fastapi

import models
import repo
from entities import HealthCareEntity
from entities import HealthCareRecordEntity
from errors import DuplicateEntryException
from errors import InvalidEntryException
from use_case import HospitalRegistrationUseCase
from use_case import register_use_case


register_hospital_use_case = register_use_case(
    HospitalRegistrationUseCase, repo.PsqlRepo
)


async def on_startup():
    await repo.start_psql_client(models.models)


router = fastapi.APIRouter(on_startup=[on_startup])


@router.post(
    "/register-center",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=HealthCareRecordEntity,
)
async def register_hospital_center(
    healthcare_data: HealthCareEntity,
):
    if not register_hospital_use_case.valid_new_entry(healthcare_data):
        raise InvalidEntryException(detail="Not a valid entry.")
    if register_hospital_use_case.duplicate_exists(healthcare_data):
        raise DuplicateEntryException(detail=f"Entry already exists.")
    return register_hospital_use_case.create_entry(healthcare_data)
