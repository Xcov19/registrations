from __future__ import annotations

import abc
from typing import Any
from typing import Awaitable
from typing import Coroutine
from typing import Protocol
from typing import Type

from registrations.domain.hospital.registration import UnclaimedHospital
from registrations.domain.hospital.registration import UnverifiedRegisteredHospital


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
    async def __aenter__(self) -> Awaitable:
        raise NotImplementedError
