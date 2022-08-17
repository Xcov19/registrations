"""A bootstrap script for di loader, env and other settings for api."""
import os

from registrations.domain.services.application_services import (
    HospitalRegistrationApplicationService,
)
from registrations.infrastructure.adapters.api.di_builder import BootStrapDI
from registrations.infrastructure.adapters.api.di_builder import DIMapping
from registrations.infrastructure.adapters.repos.dummy.repo import (
    DummyHospitalUOWAsyncImpl,
)
from registrations.infrastructure.adapters.repos.postgres_m3o.repo import (
    M3OHospitalUOWAsyncImpl,
)


def get_mapping_di() -> DIMapping:
    """Return a mapping of dependencies for the API."""
    if not (env := os.getenv("ENV")):
        raise ValueError("ENV environment variable not set.")
    if env != "test":
        return DIMapping(
            hospital_uow_async=M3OHospitalUOWAsyncImpl,
            hospital_registration_application_service=HospitalRegistrationApplicationService,
        )
    return DIMapping(
        hospital_uow_async=DummyHospitalUOWAsyncImpl,
        hospital_registration_application_service=HospitalRegistrationApplicationService,
    )


bootstrapper: BootStrapDI = BootStrapDI(mapping_di=get_mapping_di())
