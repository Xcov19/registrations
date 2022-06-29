from __future__ import annotations

import uuid
from typing import Optional
from typing import Type

import email_validator
import phonenumbers
import pydantic
from email_validator import EmailNotValidError

from registrations.domain.location.location import Address
from registrations.utils import enum_utils

# ************************************************* #
# These are the domain entities of registration..
# ************************************************* #


# Value Object
class OwnershipType(enum_utils.EnumWithItems):
    Government = "government"
    Public = "public"
    Private = "private"
    Pub_Pvt = "public_private"


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
        phonenum_obj: phonenumbers.PhoneNumber = phonenumbers.parse(phone_number)
        if not (
            phonenumbers.is_possible_number(phonenum_obj)
            and phonenumbers.is_valid_number(phonenum_obj)
        ):
            raise pydantic.ValidationError
        return phone_number


# Value Object
class ContactPerson(pydantic.BaseModel, allow_mutation=False, validate_assignment=True):
    """Key contact person registering the hospital."""

    name: str
    mobile_number: PhoneNumber
    email: Optional[pydantic.EmailStr]

    @pydantic.validator("email", pre=True)
    @classmethod
    def _validate_email(cls, email: Optional[pydantic.EmailStr]) -> pydantic.EmailStr:
        if email and not email_validator.validate_email(email):
            raise EmailNotValidError
        return email


class MissingRegistrationFieldError(pydantic.ValidationError):
    def __init__(
        self,
        error_msg: str,
        model: Type[pydantic.BaseModel],
        exc_tb: Optional[str] = None,
    ):
        error_wrapper = pydantic.error_wrappers.ErrorWrapper(
            Exception(error_msg), exc_tb or error_msg
        )
        super().__init__(errors=[error_wrapper], model=model)


class HospitalEntryAggregate(pydantic.BaseModel, validate_assignment=True):
    """Aggregate hospital entity. Not to be directly used.

    This is where you engage domain business logic for
    various entities.
    """

    hospital_id: pydantic.UUID1 = pydantic.Field(uuid.uuid1, allow_mutation=False)
    hospital_name: str
    ownership_type: Optional[OwnershipType]
    address: Address
    phone_number: PhoneNumber

    @classmethod
    def build_factory(
        cls, **kwargs
    ) -> UnclaimedHospital | UnverifiedRegisteredHospital:
        cls._validate_attributes(**kwargs)
        if cls._can_be_verified(**kwargs):
            return cls._build_unclaimed_hospital_factory(**kwargs)
        return cls._build_unverified_hospital_factory(**kwargs)

    @classmethod
    def _build_unclaimed_hospital_factory(cls, **kwargs) -> UnclaimedHospital:
        return cls.register_unclaimed_hospital_factory(**kwargs)

    @classmethod
    def _build_unverified_hospital_factory(
        cls, **kwargs
    ) -> UnverifiedRegisteredHospital:
        if not kwargs.get("key_contact_registrar"):
            raise MissingRegistrationFieldError(
                "Field missing. key_contact_registrar is required.",
                UnverifiedRegisteredHospital,
            )
        return cls.register_unverified_hospital_factory(**kwargs)

    @classmethod
    def _validate_attributes(cls, **kwargs) -> bool:
        if missing_attrs := cls._check_missing_attributes(**kwargs):
            raise AttributeError(f"Missing Attributes: {','.join(missing_attrs)}")
        return True

    @classmethod
    def _check_missing_attributes(cls, **kwargs) -> Optional[list]:
        """Check entity attributes if absent in input."""
        field_attrs = cls.__fields__.keys()
        kwarg_keys = kwargs.keys()
        return list(filter(lambda key: key not in kwarg_keys, field_attrs)) or None

    @classmethod
    def register_unverified_hospital_factory(
        cls, **kwargs
    ) -> UnverifiedRegisteredHospital:
        return UnverifiedRegisteredHospital(**kwargs)

    @classmethod
    def register_unclaimed_hospital_factory(cls, **kwargs) -> UnclaimedHospital:
        return UnclaimedHospital(**kwargs)

    @classmethod
    def _can_be_verified(
        cls,
        **kwargs,
    ) -> bool:
        """Checks if the hospital entry be verified.

        This can be used to start identification process and
        claim the hospital profile.
        """
        return UnclaimedHospital.hospital_is_verified(**kwargs)


class UnverifiedRegisteredHospital(HospitalEntryAggregate):
    """An unverified hospital that is registered."""

    key_contact_registrar: ContactPerson


class UnclaimedHospital(HospitalEntryAggregate):
    """A hospital that is not claimed by its owner."""

    verified_status: VerificationStatus

    @classmethod
    def hospital_is_verified(cls, **kwargs) -> bool:
        return (
            kwargs.get("verified_status")
            and kwargs["verified_status"] == VerificationStatus.Verified
        )
