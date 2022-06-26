import unittest
from typing import Awaitable

import pytest

from registrations.domain.hospital.registration import MissingRegistrationFieldError
from registrations.domain.hospital.registration import UnclaimedHospital
from registrations.domain.hospital.registration import UnverifiedRegisteredHospital
from registrations.domain.repo.registration_repo import InterfaceHospitalRepo
from registrations.domain.repo.registration_repo import InterfaceHospitalUOW
from registrations.domain.services.hospital_registration_services import (
    HospitalEntityType,
)
from registrations.domain.services.hospital_registration_services import (
    RegisterHospitalService,
)

# **************************************************** #
# These are plenty of inbuilt pytest fixtures. Use
# these plugins duly.
# capsys - capture system log - readout and stderr
# monkeypatch - mock an object method.
# tmpdir - stub dir like mock but you can create files.
#
# **************************************************** #


@pytest.mark.fast
class TestHospitalRegistrationServiceBuildFactory:
    """Tests the basic building blocks of hospital registration domain model."""

    def test_build_factory_valid_unverified_hospital(
        self, valid_unverified_hospital: dict
    ):
        hospital_entity: HospitalEntityType = (
            RegisterHospitalService.build_hospital_factory(**valid_unverified_hospital)
        )
        assert isinstance(hospital_entity, UnverifiedRegisteredHospital)

    def test_build_factory_invalid_unverified_hospital(
        self, invalid_unverified_hospital: dict
    ):
        with pytest.raises(
            MissingRegistrationFieldError, match=r".*Field missing.*"
        ) as exc:
            RegisterHospitalService.build_hospital_factory(
                **invalid_unverified_hospital
            )
            assert "key_contact_registrar is required" in exc.value

    def test_build_factory_valid_unclaimed_hospital(
        self, valid_unclaimed_hospital: dict
    ):
        hospital_entity: HospitalEntityType = (
            RegisterHospitalService.build_hospital_factory(**valid_unclaimed_hospital)
        )
        assert isinstance(hospital_entity, UnclaimedHospital)

    def test_build_factory_invalid_unclaimed_hospital(self, invalid_unclaimed_hospital):
        with pytest.raises(
            MissingRegistrationFieldError,
            match=r".*key_contact_registrar is required.*",
        ) as exc:
            RegisterHospitalService.build_hospital_factory(**invalid_unclaimed_hospital)
            assert "Field missing" in exc.value


class FakeSession:
    ...


class FakeHospitalRepoImpl(InterfaceHospitalRepo):
    async def save_unverified_hospital(self, **kwargs) -> UnverifiedRegisteredHospital:
        return UnverifiedRegisteredHospital(**kwargs)

    async def save_unclaimed_hospital(self, **kwargs) -> UnclaimedHospital:
        return UnclaimedHospital(**kwargs)

    async def session(self):
        return FakeSession()


class FakeHospitalUOWAsyncImpl(InterfaceHospitalUOW):

    hospital_repo = FakeHospitalRepoImpl()

    async def __aenter__(self) -> Awaitable:
        try:
            return await self.hospital_repo.session()
        except Exception as e:
            raise Exception(e, "No session defined.") from e


@pytest.mark.fast
class TestHospitalRegistrationServiceUOW:
    # TODO: Fake uow and test saving interface
    ...
