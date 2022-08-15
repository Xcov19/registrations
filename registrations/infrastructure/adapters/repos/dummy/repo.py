from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import sys
import time
from concurrent.futures import Future
from typing import Any
from typing import Literal
from typing import Optional

import pydantic

from registrations.domain.hospital import registration
from registrations.domain.repo.registration_repo import InterfaceHospitalRepo
from registrations.domain.repo.registration_repo import InterfaceHospitalUOW
from registrations.domain.repo.registration_repo import UOWSessionFlag
from registrations.utils.errors import MissingRegistrationFieldError
from registrations.utils.errors import ValidationModelType

# Get current module logger

DUMMY_DB_LOGGER = logging.getLogger(__name__)

error_stream_handler = logging.StreamHandler(stream=sys.stderr)
error_stream_handler.setLevel(logging.CRITICAL)

log_handlers = logging.StreamHandler(stream=sys.stdout)
log_handlers.setLevel(logging.INFO)

DUMMY_DB_LOGGER.addHandler(error_stream_handler)
DUMMY_DB_LOGGER.addHandler(log_handlers)


class FakeDBSession:
    """Fake database session."""

    def session(self) -> None:
        done, pending = concurrent.futures.wait(
            [
                self.__create_future(),
                self.__create_future(),
            ],
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


class DummyHospitalRepoImpl(InterfaceHospitalRepo):
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
        self, **kwargs: registration.HospitalEntryDictType
    ) -> registration.UnverifiedRegisteredHospital:
        try:
            if not isinstance(self.session, FakeDBSession):
                raise AssertionError("Should be a DB Session")
            self.session.session()
            self.__success = True
            hospital_entry = registration.HospitalEntryAggregate.build_factory(**kwargs)
            if not isinstance(
                hospital_entry, registration.UnverifiedRegisteredHospital
            ):
                raise AssertionError
            return hospital_entry
        except (pydantic.ValidationError, AttributeError) as e:
            DUMMY_DB_LOGGER.error(f"{self} Parameters are {kwargs}")
            raise e

    async def save_unclaimed_hospital(
        self, **kwargs: registration.HospitalEntryDictType
    ) -> registration.UnclaimedHospital:
        try:
            if not isinstance(self.session, FakeDBSession):
                raise AssertionError("Should be a DB Session")
            self.session.session()
            self.__success = True
            hospital_entry = registration.HospitalEntryAggregate.build_factory(**kwargs)
            if not isinstance(hospital_entry, registration.UnclaimedHospital):
                raise AssertionError
            return hospital_entry
        except pydantic.ValidationError as e:
            DUMMY_DB_LOGGER.error(f"{self} Parameters are {kwargs}")
            raise e


# **************************************************** #
# Fake hospital unit of work.
# **************************************************** #
class DummyHospitalUOWAsyncImpl(InterfaceHospitalUOW):
    hospital_repo = DummyHospitalRepoImpl()

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

    async def __aenter__(self) -> DummyHospitalUOWAsyncImpl:
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
            DUMMY_DB_LOGGER.exception(
                "Error during UOW exit.", exc_info=exc_type, stack_info=True
            )
            await self.rollback()
            await self.close()
            DUMMY_DB_LOGGER.error("Closed UOW repo session.")
            if exc_type == AttributeError:
                raise AttributeError(exc_val)
            if exc_type == MissingRegistrationFieldError:
                DUMMY_DB_LOGGER.error(
                    exc_val, exc_info=(type(exc_type), BaseException(exc_tb), None)
                )
                if isinstance(exc_val, str):
                    raise AssertionError
                model: ValidationModelType = exc_val.model
                raise MissingRegistrationFieldError(str(exc_type), model, exc_tb)
