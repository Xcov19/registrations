# Application Service
import abc
from typing import Protocol
from typing import Type

from registrations.domain.dto import HospitalRegistrationEntry
from registrations.domain.services import hospital_registration_services


class InterfaceLookAheadService(Protocol):
    """Look ahead service for already registered hospitals."""

    @classmethod
    @abc.abstractmethod
    async def lookup_search(
        cls, search_query: str
    ) -> list[hospital_registration_services.HospitalEntityType]:
        """Returns a list of search results."""
        raise NotImplementedError


# Application Service for CRUD-like calls.
class HospitalRegistrationApplicationService:
    """Application service for hospital registration."""

    @classmethod
    async def register_hospital(
        cls,
        hospital_uow_async: Type[hospital_registration_services.InterfaceHospitalUOW],
        registration_entry: HospitalRegistrationEntry,
    ) -> HospitalRegistrationEntry:
        """Registers a hospital."""
        hospital_entry = registration_entry.build_hospital_entity()
        await hospital_registration_services.RegisterHospitalService.register_hospital(
            hospital_uow_async, hospital_entry
        )
        return registration_entry
