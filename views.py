import fastapi

import models
import repo
import settings
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


async def on_shutdown():
    if settings.DEBUG:
        await repo.drop_psql_client(models.models)


router = fastapi.APIRouter(
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)


@router.post(
    "/register-center",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=HealthCareRecordEntity,
)
async def register_hospital_center(
    healthcare_data: HealthCareEntity,
):
    # TODO: refactor this error check into a
    #  separate use case method and write test.
    exclude_fields = {
        "location",
        "registering_user_info",
    }
    # validate data
    test_healthcare_data = healthcare_data.copy(deep=True, exclude=exclude_fields)
    if not await register_hospital_use_case.valid_new_entry(test_healthcare_data):
        raise InvalidEntryException(detail="Not a valid entry.")
    if await register_hospital_use_case.duplicate_exists(test_healthcare_data):
        raise DuplicateEntryException(detail=f"Entry already exists.")
    return await register_hospital_use_case.create_entry(healthcare_data)
