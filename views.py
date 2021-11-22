import fastapi

import models
import repo
import settings
from entities import HealthCareEntity
from entities import HealthCareRecordEntity
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
    return await register_hospital_use_case.save(healthcare_data)
