# Application Service
import abc
from typing import Protocol, Type

from registrations.domain.dto import ToHospitalRegistrationEntry
from registrations.domain.hospital import registration
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
        registration_entry: ToHospitalRegistrationEntry,
    ) -> ToHospitalRegistrationEntry:
        """Registers a hospital."""
        hospital_entry_dict = registration_entry.build_hospital_entity_dict()
        # Most of the domain attributes will be validated by the pydantic library
        # for the relevant entry via RegisterHospitalService.
        hospital_entry = hospital_registration_services.RegisterHospitalService.build_hospital_factory(
            **hospital_entry_dict
        )
        await hospital_registration_services.RegisterHospitalService.register_hospital(
            hospital_uow_async, hospital_entry
        )
        return registration_entry
