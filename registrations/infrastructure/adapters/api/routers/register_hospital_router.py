from __future__ import annotations

import fastapi

from registrations.domain.dto import (
    ToHospitalRegistrationEntry,
)
from registrations.infrastructure.adapters.api.di_builder import BootStrapDI
from registrations.infrastructure.adapters.repos.dummy.repo import (
    DummyHospitalUOWAsyncImpl,
)

router = fastapi.APIRouter(
    tags=["hospitals", "registration"],
)


bootstrapper = BootStrapDI(uow_di=DummyHospitalUOWAsyncImpl)


@router.on_event("startup")
def startup() -> None:
    bootstrapper.run()


@router.on_event("shutdown")
async def shutdown() -> None:
    await bootstrapper.shutdown()


@router.post(
    "/register-hospital",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=ToHospitalRegistrationEntry,
)
async def register_hospital_center(
    healthcare_data: ToHospitalRegistrationEntry,
) -> ToHospitalRegistrationEntry:
    if bootstrapper.uow is not None:
        await bootstrapper.registration_service.register_hospital(
            bootstrapper.uow, healthcare_data
        )
    return healthcare_data
