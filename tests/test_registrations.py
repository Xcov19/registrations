from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import sys
import time
from concurrent.futures import Future
from typing import Any, Literal, Optional
from unittest import mock

import pydantic
import pytest

from registrations.domain import dto
from registrations.domain.hospital.registration import (
    HospitalEntryAggregate,
    HospitalEntryDictType,
    UnclaimedHospital,
    UnverifiedRegisteredHospital,
)
from registrations.domain.repo.registration_repo import (
    InterfaceHospitalRepo,
    InterfaceHospitalUOW,
    UOWSessionFlag,
)
from registrations.domain.services.application_services import (
    HospitalRegistrationApplicationService,
)
from registrations.domain.services.hospital_registration_services import (
    HospitalEntityType,
    RegisterHospitalService,
)
from registrations.utils.errors import (
    MissingRegistrationFieldError,
    ValidationModelType,
)

# **************************************************** #
# These are plenty of inbuilt pytest fixtures. Use
# these plugins duly.
# capsys - capture system log - readout and stderr
# monkeypatch - mock an object method.
# tmpdir - stub dir like mock but you can create files.
#
# **************************************************** #

# Get current module logger
TEST_LOGGER = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setLevel(logging.CRITICAL)
TEST_LOGGER.addHandler(stream_handler)

# **************************************************** #
# To unit test the hospital registration service,
# we need to mock the hospital repository.
# **************************************************** #
class FakeDBSession:
    """Fake a database session."""

    def session(self) -> None:
        done, pending = concurrent.futures.wait(
            [self.__create_future()],
            timeout=2,
            return_when=concurrent.futures.ALL_COMPLETED,
        )
        if pending:
            raise concurrent.futures.TimeoutError("Pending future Timeout.")
        for each_future in done:
            each_future.result()

    @staticmethod
    def __create_future() -> Future:
        def _sleep(sec: int | float) -> Any:
            print(f"Creating Concurrent Future & sleeping for {sec} seconds.")
            return time.sleep(sec)

        with concurrent.futures.ThreadPoolExecutor() as t_executor:
            return t_executor.submit(_sleep, 2)


class FakeHospitalRepoImpl(InterfaceHospitalRepo):
    def __init__(self, db_session: Optional[FakeDBSession] = None):
        self.__session = db_session
        self.__success = False

    @property
    def is_successful(self) -> bool:
        """A test indicator whether fake session executed successfully."""
        return self.__success

    @property
    def session(self) -> FakeDBSession | None:
        return self.__session

    def set_session(self, db_session: FakeDBSession) -> None:
        self.__session = db_session

    async def save_unverified_hospital(
        self, **kwargs: HospitalEntryDictType
    ) -> UnverifiedRegisteredHospital:
        try:
            if not isinstance(self.session, FakeDBSession):
                raise AssertionError("Should be a DB Session")
            self.session.session()
            TEST_LOGGER.error(f"{self} Parameters are {kwargs}")
            self.__success = True
            hospital_entry = HospitalEntryAggregate.build_factory(**kwargs)
            if not isinstance(hospital_entry, UnverifiedRegisteredHospital):
                raise AssertionError
            return hospital_entry
        except (pydantic.ValidationError, AttributeError) as e:
            raise e

    async def save_unclaimed_hospital(
        self, **kwargs: HospitalEntryDictType
    ) -> UnclaimedHospital:
        try:
            if not isinstance(self.session, FakeDBSession):
                raise AssertionError("Should be a DB Session")
            self.session.session()
            TEST_LOGGER.error(f"{self} Parameters are {kwargs}")
            self.__success = True
            hospital_entry = HospitalEntryAggregate.build_factory(**kwargs)
            if not isinstance(hospital_entry, UnclaimedHospital):
                raise AssertionError
            return hospital_entry
        except pydantic.ValidationError as e:
            raise e


# **************************************************** #
# To unit test the hospital registration service,
# we need to mock the hospital unit of work.
# **************************************************** #
class FakeHospitalUOWAsyncImpl(InterfaceHospitalUOW):
    hospital_repo = FakeHospitalRepoImpl()

    def __init__(self) -> None:
        print("Creating FakeDBSession.")
        self._db_session = FakeDBSession()
        print("Created FakeDBSession.")

    async def commit(self) -> Literal[UOWSessionFlag.COMMITTED]:
        """Commit the unit of work."""
        print("Committing unit of work")
        return UOWSessionFlag.COMMITTED

    async def rollback(self) -> Literal[UOWSessionFlag.ROLLED_BACK]:
        """Rollback the unit of work."""
        print("Rolling back unit of work")
        return UOWSessionFlag.ROLLED_BACK

    async def close(self) -> Literal[UOWSessionFlag.CLOSED]:
        """Close the unit of work."""
        print("Closing UOW repo session")
        await asyncio.sleep(2)
        return UOWSessionFlag.CLOSED

    async def __aenter__(self) -> FakeHospitalUOWAsyncImpl:
        """Create a storage session using unit of work."""
        try:
            print("Setting db_session to UOW repo.")
            self.hospital_repo.set_session(self._db_session)
            return self
        except (AttributeError, pydantic.ValidationError) as e:
            await self.close()
            raise e

    async def __aexit__(
        self,
        exc_type: Exception,
        exc_val: str | MissingRegistrationFieldError,
        exc_tb: str,
    ) -> None:
        """Exit context manager."""
        await self.commit()
        if exc_val:
            TEST_LOGGER.exception(
                "Error during UOW exit.", exc_info=exc_type, stack_info=True
            )
            await self.rollback()
            await self.close()
            TEST_LOGGER.error("Closed UOW repo session.")
            if exc_type == AttributeError:
                raise AttributeError(exc_val)
            if exc_type == MissingRegistrationFieldError:
                TEST_LOGGER.error(
                    exc_val, exc_info=(type(exc_type), BaseException(exc_tb), None)
                )
                if isinstance(exc_val, str):
                    raise AssertionError
                model: ValidationModelType = exc_val.model
                raise MissingRegistrationFieldError(str(exc_type), model, exc_tb)


# **************************************************** #
# Arrange fixture for uow.
# We mock the unit of work using the mock library to
# assert the expected behaviour.
# **************************************************** #
@pytest.fixture
def repo_stub() -> FakeHospitalRepoImpl:
    return mock.MagicMock(
        spec_set=FakeHospitalRepoImpl,
        return_value=FakeHospitalRepoImpl(),
    )


@pytest.fixture
def uow_stub() -> mock.Mock:
    return mock.Mock(
        spec_set=FakeHospitalUOWAsyncImpl,
        side_effect=FakeHospitalUOWAsyncImpl,
    )


# **************************************************** #
# Use pytest -m fast to run the tests in fast mode.
# Use pytest -s to see the test debug output like print.
# **************************************************** #
@pytest.mark.fast
@pytest.mark.usefixtures("anyio_backend")
class TestHospitalRegistrationUOW:
    """Tests the hospital registration service unit of work."""

    async def test_register_hospital_uow_save_unverified_hospital(
        self,
        valid_unverified_hospital: dict,
        uow_stub: mock.Mock,
        repo_stub: FakeHospitalRepoImpl,
    ) -> None:
        async with uow_stub() as uow_ctx:
            with mock.patch.object(
                uow_ctx, "hospital_repo", spec_set=True, autospec=True, wraps=repo_stub
            ):
                if not isinstance(uow_ctx.hospital_repo, FakeHospitalRepoImpl):
                    raise AssertionError
                await uow_ctx.hospital_repo.save_unverified_hospital(
                    **valid_unverified_hospital
                )
                uow_stub.assert_called_once()

    async def test_register_hospital_uow_invalid_save_unverified_hospital(
        self, invalid_unverified_hospital: dict
    ) -> None:
        with pytest.raises(
            MissingRegistrationFieldError, match=".+validation error.+"
        ) as exc:
            async with FakeHospitalUOWAsyncImpl() as uow_ctx:
                if not isinstance(uow_ctx.hospital_repo, FakeHospitalRepoImpl):
                    raise AssertionError
                await uow_ctx.hospital_repo.save_unverified_hospital(
                    **invalid_unverified_hospital
                )
            assert exc.value.model == UnverifiedRegisteredHospital


@pytest.mark.fast
@pytest.mark.usefixtures("anyio_backend")
class TestHospitalRegistrationService:
    """Tests hospital registration service."""

    def test_build_factory_valid_unverified_hospital(
        self, valid_unverified_hospital: dict
    ) -> None:
        hospital_entity: HospitalEntityType = (
            RegisterHospitalService.build_hospital_factory(**valid_unverified_hospital)
        )
        assert isinstance(hospital_entity, UnverifiedRegisteredHospital)

    def test_build_factory_invalid_unverified_hospital(
        self, invalid_unverified_hospital: dict
    ) -> None:
        with pytest.raises(
            MissingRegistrationFieldError, match=r".*Field missing.*"
        ) as exc:
            RegisterHospitalService.build_hospital_factory(
                **invalid_unverified_hospital
            )
            assert "key_contact_registrar is required" in exc.value

    def test_build_factory_valid_unclaimed_hospital(
        self, valid_unclaimed_hospital: dict
    ) -> None:
        hospital_entity: HospitalEntityType = (
            RegisterHospitalService.build_hospital_factory(**valid_unclaimed_hospital)
        )
        assert isinstance(hospital_entity, UnclaimedHospital)

    def test_build_factory_invalid_unclaimed_hospital(
        self, invalid_unclaimed_hospital: dict
    ) -> None:
        with pytest.raises(
            MissingRegistrationFieldError,
            match=r".*key_contact_registrar is required.*",
        ) as exc:
            RegisterHospitalService.build_hospital_factory(**invalid_unclaimed_hospital)
            assert "Field missing" in exc.value

    async def test_register_unverified_hospital(
        self,
        valid_unverified_hospital: dict,
        uow_stub: mock.Mock,
        repo_stub: FakeHospitalRepoImpl,
    ) -> None:
        hospital_entity: HospitalEntityType = (
            RegisterHospitalService.build_hospital_factory(**valid_unverified_hospital)
        )
        await RegisterHospitalService.register_hospital(uow_stub, hospital_entity)
        uow_stub.assert_called_once()

    async def test_register_unclaimed_hospital(
        self,
        valid_unclaimed_hospital: dict,
        uow_stub: mock.Mock,
        repo_stub: FakeHospitalRepoImpl,
    ) -> None:
        hospital_entity: HospitalEntityType = (
            RegisterHospitalService.build_hospital_factory(**valid_unclaimed_hospital)
        )
        await RegisterHospitalService.register_hospital(uow_stub, hospital_entity)
        uow_stub.assert_called_once()


@pytest.mark.fast
@pytest.mark.usefixtures("anyio_backend")
class TestHospitalRegistrationApplicationService:
    """Tests application service for hospital registration."""

    async def test_register_hospital_manual_verification(
        self, registration_entry_manual_verification: dto.ToHospitalRegistrationEntry
    ) -> None:
        repo_instance = FakeHospitalRepoImpl(FakeDBSession())
        with mock.patch.object(
            FakeHospitalUOWAsyncImpl,
            "hospital_repo",
            spec_set=True,
            wraps=repo_instance,
        ) as hospital_repo_mock:
            await HospitalRegistrationApplicationService.register_hospital(
                FakeHospitalUOWAsyncImpl, registration_entry_manual_verification
            )
            hospital_repo_mock.save_unverified_hospital.assert_called_once()
            assert repo_instance.is_successful is True

    async def test_register_hospital_unclaimed(
        self, registration_entry_unclaimed: dto.ToHospitalRegistrationEntry
    ) -> None:
        repo_instance = FakeHospitalRepoImpl(FakeDBSession())
        with mock.patch.object(
            FakeHospitalUOWAsyncImpl,
            "hospital_repo",
            spec_set=True,
            wraps=repo_instance,
        ) as hospital_repo_mock:
            await HospitalRegistrationApplicationService.register_hospital(
                FakeHospitalUOWAsyncImpl, registration_entry_unclaimed
            )
            hospital_repo_mock.save_unclaimed_hospital.assert_called_once()
            assert repo_instance.is_successful is True
