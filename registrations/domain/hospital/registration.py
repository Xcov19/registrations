from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, Optional, Union

import email_validator
import phonenumbers
import pydantic
from email_validator import EmailNotValidError
from phonenumbers import parse as parse_number

from registrations.domain.location.location import Address, AddressGeoLocation
from registrations.utils import enum_utils
from registrations.utils.errors import MissingRegistrationFieldError

# ************************************************* #
# These are the domain entities of registration..
# ************************************************* #


# Value Object
class OwnershipType(enum_utils.EnumWithItems):
    Government = "government"
    Public = "public"
    Private = "private"
    Pub_Pvt = "public_private"
    Charitable = "charitable"


# Value Object
class VerificationStatus(enum_utils.EnumWithItems):
    Verified = "verified"
    Unverified = "unverified"
    Pending = "verification_pending"


# Value Object
class PhoneNumber(pydantic.BaseModel, allow_mutation=False, validate_assignment=True):
    number: str

    @pydantic.validator("number", pre=True)
    @classmethod
    def _validate_number(cls, phone_number: str) -> str:
        phonenum_obj: phonenumbers.PhoneNumber = parse_number(phone_number)  # type: ignore[no-any-unimported]
        if not (
            phonenumbers.is_possible_number(phonenum_obj)
            and phonenumbers.is_valid_number(phonenum_obj)
        ):
            raise MissingRegistrationFieldError("Invalid number format.", cls)
        return phone_number


# Value Object
class ContactPerson(
    pydantic.BaseModel,
    extra=pydantic.Extra.forbid,
    allow_mutation=False,
    validate_assignment=True,
):
    """Key contact person registering the hospital."""

    name: str
    mobile_number: PhoneNumber
    email: Optional[pydantic.EmailStr]

    @pydantic.validator("email", pre=True)
    @classmethod
    def _validate_email(
        cls, email: Optional[pydantic.EmailStr]
    ) -> Optional[pydantic.EmailStr]:
        if email and not email_validator.validate_email(email):
            raise EmailNotValidError
        return email


# ================================================== #
# Fix for incompatible type.
# See: https://github.com/python/mypy/issues/5382
# Fixes error of type:
# Argument 1 to <Some Caller> has incompatible type "**Dict[str, <Data types>]";
# expected...
# TypeDict and Final does not fix this.
# ================================================== #
HospitalEntryDictType = Union[
    pydantic.UUID1,
    str,
    Optional[OwnershipType],
    Address,
    PhoneNumber,
    Optional[AddressGeoLocation],
    datetime.datetime,
    ContactPerson,
    Optional[VerificationStatus],
]


class HospitalEntryAggregate(pydantic.BaseModel, validate_assignment=True):
    """Aggregate hospital entity. Not to be directly used.

    This is where you engage domain business logic for
    various entities.
    """

    hospital_id: pydantic.UUID1 = pydantic.Field(
        default_factory=uuid.uuid1, allow_mutation=False
    )
    hospital_name: str
    ownership_type: Optional[OwnershipType]
    address: Address
    phone_number: PhoneNumber
    # TODO: needs to be test covered in application service.
    geo_location: Optional[AddressGeoLocation]
    added_since: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now, allow_mutation=False
    )

    @classmethod
    def build_factory(cls, **kwargs: HospitalEntryDictType) -> HospitalEntityType:
        return (
            cls._build_unclaimed_hospital_factory(**kwargs)
            if cls._can_be_verified(**kwargs)
            else cls._build_unverified_hospital_factory(**kwargs)
        )

    @classmethod
    def _build_unclaimed_hospital_factory(
        cls, **kwargs: HospitalEntryDictType
    ) -> UnclaimedHospital:
        # Required to typecase the expectation
        # of kwargs to have any type.
        values_dict: Dict[str, Any] = kwargs
        return UnclaimedHospital(**values_dict)

    @classmethod
    def _build_unverified_hospital_factory(
        cls, **kwargs: HospitalEntryDictType
    ) -> UnverifiedRegisteredHospital:
        if not kwargs.get("key_contact_registrar"):
            raise MissingRegistrationFieldError(
                "Field missing. key_contact_registrar is required.",
                UnverifiedRegisteredHospital,
            )
        # Required to typecase the expectation
        # of kwargs to have any type.
        values_dict: Dict[str, Any] = kwargs
        return UnverifiedRegisteredHospital(**values_dict)

    @pydantic.root_validator
    @classmethod
    def _validate_attributes(cls, values: dict) -> dict:
        if missing_attrs := cls._check_missing_attributes(**values):
            raise AttributeError(f"Missing Attributes: {','.join(missing_attrs)}")
        return values

    @classmethod
    def _check_missing_attributes(cls, **kwargs: str) -> Optional[list]:
        """Check entity attributes if absent in input."""
        field_attrs = cls.__fields__.keys()
        kwarg_keys = kwargs.keys()
        return list(filter(lambda key: key not in kwarg_keys, field_attrs)) or None

    @classmethod
    def _can_be_verified(
        cls,
        **kwargs: HospitalEntryDictType,
    ) -> bool:
        """Checks if the hospital entry can be verified.

        This can be used to start identification process and
        claim the hospital profile.
        """
        return UnclaimedHospital.hospital_is_verified(
            **kwargs
        ) or UnclaimedHospital.hospital_verification_pending(**kwargs)


class UnverifiedRegisteredHospital(HospitalEntryAggregate):
    """An unverified hospital that is registered."""

    key_contact_registrar: ContactPerson


class UnclaimedHospital(HospitalEntryAggregate):
    """A hospital that is not claimed by its owner."""

    verified_status: VerificationStatus

    @classmethod
    def hospital_is_verified(cls, **kwargs: HospitalEntryDictType) -> bool:
        return (
            bool(kwargs.get("verified_status"))
            and kwargs["verified_status"] == VerificationStatus.Verified
        )

    @classmethod
    def hospital_verification_pending(cls, **kwargs: HospitalEntryDictType) -> bool:
        return (
            bool(kwargs.get("verified_status"))
            and kwargs["verified_status"] == VerificationStatus.Pending
        )


# ************************************************* #
# Avoid errors like:
# Incompatible return type:
# Expected UnverifiedRegisteredHospital but got typing.Union[UnclaimedHospital, UnverifiedRegisteredHospital].
# ************************************************* #
HospitalEntityType = Union[UnclaimedHospital, UnverifiedRegisteredHospital]
