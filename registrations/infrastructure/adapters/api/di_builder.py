"""Dependency injection builder for dependencies to run API."""
from __future__ import annotations

from typing import Optional, Protocol, Type, runtime_checkable

from registrations.domain.repo.registration_repo import InterfaceHospitalUOW
from registrations.domain.services.application_services import (
    InterfaceRegistrationService,
)


@runtime_checkable
class InterfaceDIMapping(Protocol):

    hospital_uow_async: Type[InterfaceHospitalUOW]
    hospital_registration_application_service: Type[InterfaceRegistrationService]


class DIMapping(InterfaceDIMapping):
    """Dependency injection mapping for API.

    Add dependency fields for uows, services as needed.
    If more services are added, add them to the services list below.
    They should then be mapped to initial values in the mapping_di.
    """

    def __init__(
        self,
        hospital_uow_async: Type[InterfaceHospitalUOW],
        hospital_registration_application_service: Type[InterfaceRegistrationService],
    ):

        self.hospital_uow_async = hospital_uow_async
        self.hospital_registration_application_service = (
            hospital_registration_application_service
        )


class BootStrapDI:
    """A DI wrapper service specific to fastapi."""

    def __init__(self, mapping_di: DIMapping):
        self.uow: Optional[Type[InterfaceHospitalUOW]] = mapping_di.hospital_uow_async
        # HospitalRegistrationApplicationService
        self.registration_service = mapping_di.hospital_registration_application_service

    def run(self) -> None:
        # TODO: wrap a singleton around self.uow class
        #  so it doesn't have to start up every time.
        ...

    async def shutdown(self) -> None:
        """Shutdown consumed services."""
        if self.uow is not None:
            await self.uow().close()
            self.uow = None
