import fastapi
import models
from entities import HealthCareEntity, HealthCareRecordEntity

import repo
import settings
from use_case import HospitalRegistrationUseCase, register_use_case

register_hospital_use_case = register_use_case(
    HospitalRegistrationUseCase, repo.PsqlRepo
)


async def on_startup():
    if settings.ENV_CLASS.debug:
        await models.start_psql_client(models.models)


async def on_shutdown():
    if settings.ENV_CLASS.debug:
        await models.drop_psql_client(models.models)


router = fastapi.APIRouter(
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    tags=["covid hospitals", "user", "sso", "feedback", "survey-forms"],
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
