"""Data transfer object for hospital domain registration."""
from __future__ import annotations

from typing import Optional

import pydantic

from registrations.domain.hospital import registration
from registrations.domain.location.location import Address
from registrations.utils import enum_utils
from registrations.utils.errors import InvalidRegistrationEntryError


class RegisterKeyContact(
    pydantic.BaseModel,
    extra=pydantic.Extra.forbid,
    allow_mutation=False,
    validate_assignment=True,
    arbitrary_types_allowed=False,
):
    """Key contact person registering hospital."""

    name: str
    mobile: str
    email: Optional[pydantic.EmailStr]


class ToHospitalRegistrationEntry(
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
        split_names = name.strip().split()
        valid_conditions = split_names and (
            any(len(word) >= 2 for word in split_names)
            or (len(split_names) == 1 and len(name.strip().split()[0]) >= 3)
        )
        if not valid_conditions:
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
        wrong_invariant = not key_contact and not verified_status
        wrong_invariant = wrong_invariant or bool(
            verified_status
            and (
                (
                    verified_status
                    == enum_utils.enum_value_of(
                        registration.VerificationStatus.Unverified
                    )
                    and not key_contact
                )
                or (
                    verified_status
                    != enum_utils.enum_value_of(
                        registration.VerificationStatus.Unverified
                    )
                    and key_contact
                )
            )
        )
        if wrong_invariant:
            error_msg = (
                f"Cannot have {verified_status} verification status with "
                f"{(key_contact and key_contact.name) or key_contact} key contact."
            )
            raise InvalidRegistrationEntryError(error_msg)
        return values

    def build_hospital_entity_dict(self) -> dict:
        """Build hospital entity.

        :return: dict, the hospital entity dict to register.
        """
        builder_dict = self.dict()
        if verified_status := builder_dict.get("verified_status"):
            builder_dict["verified_status"] = registration.VerificationStatus(
                verified_status
            )
        if key_contact := builder_dict.pop("key_contact", None):
            builder_dict["key_contact_registrar"] = registration.ContactPerson(
                name=key_contact.get("name"),
                mobile_number=registration.PhoneNumber(
                    number=key_contact.get("mobile")
                ),
                email=key_contact.get("email"),
            )
        builder_dict["phone_number"] = registration.PhoneNumber(
            number=builder_dict.pop("hospital_contact_number")
        )
        builder_dict["hospital_name"] = builder_dict.pop("name")
        return builder_dict
