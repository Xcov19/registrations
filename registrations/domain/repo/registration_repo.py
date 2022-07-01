from __future__ import annotations

import abc
import enum
from typing import Protocol

from registrations.domain.hospital.registration import UnclaimedHospital
from registrations.domain.hospital.registration import UnverifiedRegisteredHospital


class UOWSessionFlag(enum.Enum):
    """Session flags for UOW."""

    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


class InterfaceHospitalRepo(Protocol):
    @abc.abstractmethod
    async def save_unverified_hospital(self, **kwargs) -> UnverifiedRegisteredHospital:
        raise NotImplementedError

    @abc.abstractmethod
    async def save_unclaimed_hospital(self, **kwargs) -> UnclaimedHospital:
        raise NotImplementedError


class InterfaceHospitalUOW(Protocol):

    hospital_repo: InterfaceHospitalRepo

    # This is perfect!: https://stackoverflow.com/a/68712168/2290820
    @abc.abstractmethod
    async def __aenter__(self) -> InterfaceHospitalUOW:
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self) -> UOWSessionFlag.COMMITTED:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> UOWSessionFlag.ROLLED_BACK:
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self):
        raise NotImplementedError
