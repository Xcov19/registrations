"""Data transfer object for hospital domain registration."""
from __future__ import annotations

from typing import Optional

import pydantic

from registrations.domain.hospital import registration
from registrations.domain.location.location import Address
from registrations.domain.services import hospital_registration_services
from registrations.utils import enum_utils


class RegisterKeyContact(
    pydantic.BaseModel,
    allow_mutation=False,
    validate_assignment=True,
    arbitrary_types_allowed=False,
):
    """Key contact person registering hospital."""

    name: str
    mobile: str
    email: Optional[pydantic.EmailStr]


class HospitalRegistrationEntry(
    pydantic.BaseModel,
    allow_mutation=False,
    validate_assignment=True,
    arbitrary_types_allowed=False,
):
    """Hospital registration details."""

    name: str
    ownership_type: str
    hospital_contact_number: str
    key_contact: Optional[RegisterKeyContact]
    verified_status: Optional[str]
    address: Address

    @pydantic.validator("ownership_type", pre=True)
    @classmethod
    def validate_ownership_type(cls, ownership_type: str) -> str:
        """Validate ownership is limited to OwnershipType enum."""
        if ownership_type not in registration.OwnershipType.values():
            raise ValueError(f"Invalid ownership type: {ownership_type}")
        return ownership_type

    @pydantic.validator("name", pre=True)
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate name has atleast one word with 3 characters."""
        if not (name and len(name.strip().split()[0]) >= 3):
            raise ValueError(f"Invalid name: {name}. Not enough characters.")
        return name

    @pydantic.root_validator
    @classmethod
    def validate_hospital_entity(cls, values: dict) -> dict:
        """Validate hospital entity.

        We either get a verification status or an unverified
        manual registration entry. We cannot get both.
        Either attribute should be accessible via registration_entry
        as verified_status or key_contact.
        """
        verified_status = values.get("verified_status")
        key_contact: Optional[RegisterKeyContact] = values.get("key_contact")
        if (
            verified_status
            == enum_utils.enum_value_of(registration.VerificationStatus.Unverified)
            and not key_contact
        ) or (
            verified_status
            != enum_utils.enum_value_of(registration.VerificationStatus.Unverified)
            and key_contact
        ):
            error_msg = (
                f"Cannot have {verified_status} verification status with "
                f"{(key_contact and key_contact.name) or key_contact} key contact."
            )
            raise ValueError(error_msg)
        return values

    def build_hospital_entity(self) -> registration.HospitalEntityType:
        """Build hospital entity.

        :return: HospitalEntityType, the hospital entity to register.
        """
        builder_dict = self.dict()
        if verified_status := builder_dict.get("verified_status"):
            builder_dict["verified_status"] = registration.VerificationStatus(
                verified_status
            )
        if key_contact := builder_dict.pop("key_contact", None):
            builder_dict["key_contact_registrar"] = key_contact
        builder_dict["phone_number"] = registration.PhoneNumber(
            number=builder_dict.pop("hospital_contact_number")
        )
        # Most of the domain attributes will be validated by the pydantic library
        # for the relevant entry via RegisterHospitalService.
        return hospital_registration_services.RegisterHospitalService.build_hospital_factory(
            **builder_dict
        )
