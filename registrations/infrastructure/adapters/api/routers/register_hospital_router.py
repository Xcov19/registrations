from __future__ import annotations

import fastapi

from registrations.domain.dto import ToHospitalRegistrationEntry
from registrations.infrastructure.adapters.api import bootstrap

router = fastapi.APIRouter(
    tags=["hospitals", "registration"],
)


@router.post(
    "/register-hospital",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=ToHospitalRegistrationEntry,
)
async def register_hospital_center(
    healthcare_data: ToHospitalRegistrationEntry,
) -> ToHospitalRegistrationEntry:
    if bootstrap.bootstrapper.uow is not None:
        await bootstrap.bootstrapper.registration_service.register_hospital(
            bootstrap.bootstrapper.uow, healthcare_data
        )
    return healthcare_data
