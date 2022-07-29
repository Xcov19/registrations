from __future__ import annotations

import abc
import enum
from typing import Literal
from typing import Protocol

from registrations.domain.hospital.registration import HospitalEntityType
from registrations.domain.hospital.registration import UnclaimedHospital
from registrations.domain.hospital.registration import UnverifiedRegisteredHospital
from registrations.utils.errors import MissingRegistrationFieldError


class UOWSessionFlag(enum.Enum):
    """Session flags for UOW."""

    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    CLOSED = "closed"


class InterfaceHospitalRepo(Protocol):
    @abc.abstractmethod
    async def save_unverified_hospital(
        self, **kwargs: str
    ) -> UnverifiedRegisteredHospital:
        raise NotImplementedError

    @abc.abstractmethod
    async def save_unclaimed_hospital(self, **kwargs: str) -> UnclaimedHospital:
        raise NotImplementedError


class InterfaceHospitalUOW(Protocol):

    hospital_repo: InterfaceHospitalRepo

    # This is perfect!: https://stackoverflow.com/a/68712168/2290820
    @abc.abstractmethod
    async def __aenter__(self) -> InterfaceHospitalUOW:
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(
        self,
        exc_type: Exception,
        exc_val: str | MissingRegistrationFieldError,
        exc_tb: str,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self) -> Literal[UOWSessionFlag.COMMITTED]:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> Literal[UOWSessionFlag.ROLLED_BACK]:
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self) -> Literal[UOWSessionFlag.CLOSED]:
        raise NotImplementedError
