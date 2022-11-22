from __future__ import annotations

import abc
from typing import Protocol, Type, TypeVar

import pydantic

from registrations.domain.hospital.registration import (
    HospitalEntityType,
    HospitalEntryAggregate,
    HospitalEntryDictType,
    UnclaimedHospital,
    UnverifiedRegisteredHospital,
)
from registrations.domain.repo.registration_repo import InterfaceHospitalUOW

# ************************************************* #
# These are the infra, domain & application services
# for domain entities of registration.
# Contains interface(ports) definition and implementation.
# ************************************************* #

# See: https://github.com/python/mypy/issues/5374#issuecomment-406218346
IHUOW = TypeVar("IHUOW", bound=Type[InterfaceHospitalUOW])


class InterfaceEmailVerificationService(Protocol):
    """Infrastructure service interface for email verification."""

    @classmethod
    @abc.abstractmethod
    def is_valid_domain(cls, email: pydantic.EmailStr) -> bool:
        """Checks if domain is valid."""
        raise NotImplementedError


class InterfaceMobileNumberVerificationService(Protocol):
    """Infrastructure service interface for mobile verification."""

    @classmethod
    @abc.abstractmethod
    def check_valid_format(cls, mobile: pydantic.PositiveInt) -> bool:
        """Checks if mobile has valid format."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def send_otp(cls, mobile: pydantic.PositiveInt) -> pydantic.PositiveInt:
        """Generates and sends a valid TOTP."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def verify_otp(
        cls, mobile: pydantic.PositiveInt, otp: pydantic.PositiveInt
    ) -> bool:
        """Verifies a valid OTP."""
        raise NotImplementedError


# Domain service
class RegisterHospitalService:
    """Register unverified hospital manually or imported but unclaimed."""

    @classmethod
    def build_hospital_factory(
        cls, **kwargs: HospitalEntryDictType
    ) -> HospitalEntityType:
        """Stores hospital entity based on available attributes."""
        return HospitalEntryAggregate.build_factory(**kwargs)

    @classmethod
    async def register_hospital(
        cls,
        hospital_uow_async: IHUOW,
        hospital_entry: HospitalEntityType,
    ) -> None:
        if isinstance(hospital_entry, UnclaimedHospital):
            await cls.register_unclaimed_hospital(hospital_uow_async, hospital_entry)
        else:
            await cls.register_unverified_hospital(hospital_uow_async, hospital_entry)

    @classmethod
    async def register_unverified_hospital(
        cls,
        hospital_uow_async: Type[InterfaceHospitalUOW],
        unverified_hospital: UnverifiedRegisteredHospital,
    ) -> None:
        """Register hospital manually submitted but unverified."""
        async with hospital_uow_async() as uow_ctx:
            await uow_ctx.hospital_repo.save_unverified_hospital(
                **unverified_hospital.dict()
            )
            await uow_ctx.commit()

    @classmethod
    async def register_unclaimed_hospital(
        cls,
        hospital_uow_async: Type[InterfaceHospitalUOW],
        unclaimed_hospital: UnclaimedHospital,
    ) -> None:
        """Register  imported hospital but unclaimed and unverified.

        Note: You can verify hospital YET NOT CLAIM
        BUT TO CLAIM YOU HAVE TO VERIFY KEY CONTACT.
        Then HOSPITAL Verification happens async in the background.
        """
        async with hospital_uow_async() as uow_ctx:
            await uow_ctx.hospital_repo.save_unclaimed_hospital(
                **unclaimed_hospital.dict()
            )
            await uow_ctx.commit()
