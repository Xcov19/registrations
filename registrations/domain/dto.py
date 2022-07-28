"""Data transfer object for hospital domain registration."""
from __future__ import annotations

import datetime
import re
from typing import Optional

import pydantic

from registrations.domain.hospital import registration
from registrations.domain.location.location import Address
from registrations.domain.location.location import AddressGeoLocation
from registrations.utils import enum_utils
from registrations.utils.errors import InvalidRegistrationEntryError

DATE_TIME_REGEX = (
    r"^(\d{4}[/-]\d{2}[/-]\d{2})((T\d{2}[:/-]\d{2}[:/-]\d{2}Z)|(\s\d{2}[:/-]\d{2}[:/-]\d{2}){0,"
    r"1}(\s[+-]\d{0,4}){0,1})$"
)
DATE_TIME_RGX_COMPILE = re.compile(DATE_TIME_REGEX)


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
    geo_location: Optional[AddressGeoLocation]
    added_since: Optional[str]

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
        if split_names and (
            any(len(word) >= 2 for word in split_names)
            or (len(split_names) == 1 and len(name.strip().split()[0]) >= 3)
        ):
            return name
        raise ValueError(f"Invalid name: {name}. Not enough characters.")

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
        absent_invariants = not key_contact and not verified_status
        unverified_but_missing_key_contact = verified_status and (
            verified_status
            == enum_utils.enum_value_of(registration.VerificationStatus.Unverified)
            and not key_contact
        )
        verified_and_key_contact = verified_status and (
            verified_status
            != enum_utils.enum_value_of(registration.VerificationStatus.Unverified)
            and key_contact
        )
        if absent_invariants or bool(
            unverified_but_missing_key_contact or verified_and_key_contact
        ):
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
        if geo_location := builder_dict.pop("geo_location", None):
            builder_dict["geo_location"] = geo_location
        if added_since := builder_dict.pop("added_since", None):
            date_time = self._parse_datetime(added_since)
            builder_dict["added_since"] = date_time
        builder_dict["phone_number"] = registration.PhoneNumber(
            number=builder_dict.pop("hospital_contact_number")
        )
        builder_dict["hospital_name"] = builder_dict.pop("name")
        return builder_dict

    @staticmethod
    def _parse_datetime(added_since: str) -> datetime.datetime:
        """Return datetime formatted timestamp.

        The datetime format should be of the form:
        %Y-%m-%d [%H:%M:%S [%z]]

        :param added_since: str, date time string.
        :return: datetime.datetime, the parsed date time.
        """
        if (matched_str := DATE_TIME_RGX_COMPILE.match(added_since)) and (
            matched_group := matched_str.group()
        ):
            # Different matching group lengths have different datetime formats.
            matched_fmt_len = len(matched_group.split())
            if matched_fmt_len == 3:
                return datetime.datetime.strptime(matched_group, "%Y-%m-%d %H:%M:%S %z")
            if matched_fmt_len == 2:
                return datetime.datetime.strptime(matched_group, "%Y-%m-%d %H:%M:%S")
            _, _, _, penultimate_match, last_match = matched_str.groups()
            if matched_fmt_len == 1 and (penultimate_match is last_match is None):
                return datetime.datetime.strptime(matched_group, "%Y-%m-%dT%H:%M:%SZ")
            if matched_fmt_len == 1:
                return datetime.datetime.strptime(matched_group, "%Y-%m-%d")
        raise ValueError(f"Invalid date time format: {added_since}")
