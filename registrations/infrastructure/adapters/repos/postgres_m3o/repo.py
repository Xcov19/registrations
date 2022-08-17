from __future__ import annotations

import logging
import os
import sys
from typing import Callable
from typing import Literal

import pydantic
import requests

from registrations.domain.hospital import registration
from registrations.domain.repo.registration_repo import InterfaceHospitalRepo
from registrations.domain.repo.registration_repo import InterfaceHospitalUOW
from registrations.domain.repo.registration_repo import UOWSessionFlag
from registrations.infrastructure.adapters.repos.postgres_m3o import m3o_dto
from registrations.utils.errors import MissingRegistrationFieldError
from registrations.utils.errors import RecordAlreadyExistsError
from registrations.utils.errors import ValidationModelType

M3O_DB_LOGGER = logging.getLogger(__name__)

error_stream_handler = logging.StreamHandler(stream=sys.stderr)
error_stream_handler.setLevel(logging.CRITICAL)

log_handlers = logging.StreamHandler(stream=sys.stdout)
log_handlers.setLevel(logging.INFO)

M3O_DB_LOGGER.addHandler(error_stream_handler)
M3O_DB_LOGGER.addHandler(log_handlers)

M3O_API_TOKEN = os.getenv("M3O_API_TOKEN")


class M3OHospitalRepoImpl(InterfaceHospitalRepo):
    def __init__(self, m3o_token: str | None = None) -> None:
        self.__session_api = m3o_token
        self.__unverified_tbl = "unverified_hospital"
        self.__unclaimed_hospital = "unclaimed_hospital"
        self.pending_transaction: list[Callable] = []

    async def save_unverified_hospital(
        self, **kwargs: registration.HospitalEntryDictType
    ) -> registration.UnverifiedRegisteredHospital:
        try:
            # check if unverified hospital exists then return exists error.
            if self._record_exists(self.__unverified_tbl, **kwargs):
                raise RecordAlreadyExistsError("Record already exists.")
            hospital_entry = registration.HospitalEntryAggregate.build_factory(**kwargs)
            if not isinstance(
                hospital_entry, registration.UnverifiedRegisteredHospital
            ):
                raise AssertionError
            self.enqueue_transaction(
                self._create_record,
                self.__unverified_tbl,
                hospital_entry=hospital_entry,
            )
            return hospital_entry
        except (
            pydantic.ValidationError,
            AttributeError,
            AssertionError,
            requests.HTTPError,
        ) as e:
            M3O_DB_LOGGER.error(f"Error: {e}\n{self} Parameters are {kwargs}")
            raise e

    async def save_unclaimed_hospital(
        self, **kwargs: registration.HospitalEntryDictType
    ) -> registration.UnclaimedHospital:
        try:
            # check if unclaimed hospital exists then return exists error.
            if self._record_exists(self.__unclaimed_hospital, **kwargs):
                raise RecordAlreadyExistsError("Record already exists.")
            hospital_entry = registration.HospitalEntryAggregate.build_factory(**kwargs)
            if not isinstance(hospital_entry, registration.UnclaimedHospital):
                raise AssertionError
            self.enqueue_transaction(
                self._create_record,
                self.__unclaimed_hospital,
                hospital_entry=hospital_entry,
            )
            return hospital_entry
        except (
            pydantic.ValidationError,
            AttributeError,
            AssertionError,
            requests.HTTPError,
        ) as e:
            M3O_DB_LOGGER.error(f"Error: {e}\n{self} Parameters are {kwargs}")
            raise e

    def enqueue_transaction(
        self,
        executable: Callable,
        table: str,
        /,
        **kwargs: registration.HospitalEntityType,
    ) -> None:
        self.pending_transaction += [lambda: executable(table, **kwargs)]

    async def set_executable(self) -> None:
        for each_callable_transaction in self.pending_transaction:
            each_callable_transaction()

    @property
    def has_session_key(self) -> bool:
        """Checks if session key is set."""
        return bool(self.__session_api)

    def _record_exists(
        self, table: str, /, **kwargs: registration.HospitalEntryDictType
    ) -> bool:
        """Checks if record exists in the table."""
        url = "https://api.m3o.com/v1/db/Read"

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": f"Bearer {self.__session_api}",
        }
        address: dict[str, str | None] = {}
        hospital_name = str(kwargs.get("hospital_name"))
        ownership_type = str(kwargs.get("ownership_type"))
        if (address_dict := kwargs.get("address")) and isinstance(address_dict, dict):
            address = address_dict
        query = (
            f"ownership_type == {ownership_type} and hospital_name == {hospital_name} and "
            f"address.street == {address.get('street')} and address.city == {address.get('city')} and "
            f"address.state == {address.get('state')} and address.country == {address.get('country')}"
        )
        json_payload = {
            "table": table,
            "query": query,
        }
        response = requests.post(url, json=json_payload, headers=headers)
        if not 400 <= response.status_code <= 511 and (data := response.json()):
            return data and bool(data["records"])
        return False

    def _create_record(
        self, table: str, hospital_entry: registration.HospitalEntityType
    ) -> dict[str, str] | None:
        """Creates record in table."""
        # save entry using dto
        url = "https://api.m3o.com/v1/db/Create"
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": f"Bearer {self.__session_api}",
        }
        hospital_record_dict = m3o_dto.parse_to_dict(table, hospital_entry)
        json_payload = {"record": hospital_record_dict, "table": table}
        response = requests.post(url, json=json_payload, headers=headers)
        response.raise_for_status()
        if (json_response := response.json()) and isinstance(json_response, dict):
            return json_response
        return None


# **************************************************** #
# Hospital unit of work for M3O Postgres database.
# **************************************************** #
class M3OHospitalUOWAsyncImpl(InterfaceHospitalUOW):
    hospital_repo = M3OHospitalRepoImpl(M3O_API_TOKEN)

    async def commit(self) -> Literal[UOWSessionFlag.COMMITTED]:
        """Commit the unit of work."""
        M3O_DB_LOGGER.info("Committing unit of work")
        await self.hospital_repo.set_executable()
        M3O_DB_LOGGER.info("committed.")
        return UOWSessionFlag.COMMITTED

    async def rollback(self) -> Literal[UOWSessionFlag.ROLLED_BACK]:
        """Rollback the unit of work."""
        M3O_DB_LOGGER.error(
            "Rolling back unit of work.\nClearing pending transactions."
        )
        self.hospital_repo.pending_transaction.clear()
        return UOWSessionFlag.ROLLED_BACK

    async def close(self) -> Literal[UOWSessionFlag.CLOSED]:
        """Close the unit of work."""
        M3O_DB_LOGGER.info("Closing M3O UOW session.")
        return UOWSessionFlag.CLOSED

    async def __aenter__(self) -> M3OHospitalUOWAsyncImpl:
        """Create a storage session using unit of work."""
        try:
            M3O_DB_LOGGER.info("Setting db_session to UOW repo.")
            # TODO: These should be changed from AssertionError
            if not self.hospital_repo.has_session_key:
                raise AssertionError("Session key is not set.")
            if self.hospital_repo.pending_transaction:
                error_msg = (
                    "There are pending transactions.\n"
                    "This is atomically an error that things "
                    "did not entirely execute the last time."
                    f"{self.hospital_repo.pending_transaction}"
                )
                raise AssertionError(error_msg)
            return self
        except (AttributeError, AssertionError, pydantic.ValidationError) as e:
            M3O_DB_LOGGER.error(f"Error: {e}\n{self}", exc_info=e, stack_info=True)
            raise e

    async def __aexit__(
        self,
        exc_type: Exception,
        exc_val: str | MissingRegistrationFieldError,
        exc_tb: str,
    ) -> None:
        """Exit context manager."""
        if exc_val:
            M3O_DB_LOGGER.exception(
                "Error during UOW exit.", exc_info=exc_type, stack_info=True
            )
            await self.rollback()
            M3O_DB_LOGGER.error("Error: Closed M3O UOW session.")
            if exc_type == AttributeError:
                raise AttributeError(exc_val)
            if exc_type == MissingRegistrationFieldError:
                M3O_DB_LOGGER.error(
                    exc_val, exc_info=(type(exc_type), BaseException(exc_tb), None)
                )
                if isinstance(exc_val, str):
                    raise AssertionError
                model: ValidationModelType = exc_val.model
                raise MissingRegistrationFieldError(str(exc_type), model, exc_tb)
