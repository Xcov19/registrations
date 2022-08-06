"""Dependency injection builder for dependencies to run API."""
from typing import Optional, Type

from registrations.domain.repo.registration_repo import InterfaceHospitalUOW
from registrations.domain.services.application_services import (
    HospitalRegistrationApplicationService,
)


class BootStrapDI:
    """A DI wrapper service specific to fastapi."""

    def __init__(self, uow_di: Type[InterfaceHospitalUOW]):
        self.uow: Optional[Type[InterfaceHospitalUOW]] = uow_di
        self.registration_service = HospitalRegistrationApplicationService

    def run(self) -> None:
        # TODO: wrap a singleton around self.uow class
        #  so it doesn't have to start up every time.
        ...

    async def shutdown(self) -> None:
        """Shutdown consumed services."""
        if self.uow is not None:
            await self.uow().close()
            self.uow = None
