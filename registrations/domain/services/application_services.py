# Application Service
import abc
from typing import Protocol
from typing import Type

from registrations.domain.dto import HospitalRegistrationEntry
from registrations.domain.hospital.registration import ContactPerson
from registrations.domain.hospital.registration import PhoneNumber
from registrations.domain.hospital.registration import VerificationStatus
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
        hospital_uow_async: Type[hospital_registration_services.IUOW],
        registration_entry: HospitalRegistrationEntry,
    ) -> HospitalRegistrationEntry:
        """Registers a hospital."""
        builder_dict = {}
        # **************************************************************** #
        # We either get a verification status or an unverified
        # manual registration entry. We cannot get both.
        # Either attribute should be accessible via registration_entry
        # as verified_status or key_contact.
        # **************************************************************** #
        if registration_entry.verified_status:
            builder_dict["verified_status"] = VerificationStatus(
                registration_entry.verified_status
            )
        if registration_entry.key_contact:
            builder_dict["key_contact_registrar"] = ContactPerson(
                name=registration_entry.key_contact.name,
                mobile_number=PhoneNumber(number=registration_entry.key_contact.mobile),
                email=registration_entry.key_contact.email,
            )
        builder_dict = {
            **builder_dict,
            **dict(
                hospital_name=registration_entry.name,
                ownership_type=registration_entry.ownership_type,
                address=registration_entry.address,
                phone_number=PhoneNumber(
                    number=registration_entry.hospital_contact_number
                ),
            ),
        }
        # Most of the field attributes will be validated by the pydantic library
        # for the relevant entry via RegisterHospitalService.
        cls._validate_registration_entry(builder_dict)
        hospital_entry = hospital_registration_services.RegisterHospitalService.build_hospital_factory(
            **builder_dict
        )
        await hospital_registration_services.RegisterHospitalService.register_hospital(
            hospital_uow_async, hospital_entry
        )
        return registration_entry

    @classmethod
    def _validate_registration_entry(cls, registration_entry_dict: dict) -> bool:
        """Validates a registration entry else raises error."""
        # TODO:
        #   - validate ownership is limited to OwnershipType.
        #   - validate name has atleast one word with 3 characters.
        #   - validate entry is either verifiable and hence unclaimed or manual entry.
        #   - validate verified status if given, is one of VerificationStatus.
        return True
