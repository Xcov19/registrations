from __future__ import annotations

import abc
from typing import Protocol
from typing import Type
from typing import Union

import pydantic

from registrations.domain.hospital.registration import HospitalEntryAggregate
from registrations.domain.hospital.registration import UnclaimedHospital
from registrations.domain.hospital.registration import UnverifiedRegisteredHospital
from registrations.domain.repo.registration_repo import InterfaceHospitalUOW

# ************************************************* #
# These are the infra, domain & application services
# for domain entities of registration.
# Contains interface(ports) definition and implementation.
# ************************************************* #

IUOW = InterfaceHospitalUOW

HospitalEntityType = Union[UnclaimedHospital, UnverifiedRegisteredHospital]


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
    def build_hospital_factory(cls, **kwargs) -> HospitalEntityType:
        """Stores hospital entity based on available attributes."""
        return HospitalEntryAggregate.build_factory(**kwargs)

    @classmethod
    async def register_hospital(
        cls, hospital_uow_async: Type[IUOW], hospital_entry: HospitalEntityType
    ):
        if isinstance(hospital_entry, UnclaimedHospital):
            await cls.register_unclaimed_hospital(hospital_uow_async, hospital_entry)
        else:
            await cls.register_unverified_hospital(hospital_uow_async, hospital_entry)

    @classmethod
    async def register_unverified_hospital(
        cls,
        hospital_uow_async: Type[IUOW],
        unverified_hospital: UnverifiedRegisteredHospital,
    ):
        """Register hospital manually submitted but unverified."""
        async with hospital_uow_async() as uow_ctx:
            await uow_ctx.hospital_repo.save_unverified_hospital(
                **unverified_hospital.dict()
            )

    @classmethod
    async def register_unclaimed_hospital(
        cls, hospital_uow_async: Type[IUOW], unclaimed_hospital: UnclaimedHospital
    ):
        """Register  imported hospital but unclaimed and unverified.

        Note: You can verify hospital YET NOT CLAIM
        BUT TO CLAIM YOU HAVE TO VERIFY KEY CONTACT.
        Then HOSPITAL Verification happens async in the background.
        """
        async with hospital_uow_async() as uow_ctx:
            await uow_ctx.hospital_repo.save_unclaimed_hospital(
                **unclaimed_hospital.dict()
            )
