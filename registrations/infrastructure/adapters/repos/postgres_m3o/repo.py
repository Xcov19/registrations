from __future__ import annotations

import logging
import os
import sys
from typing import Callable
from typing import Optional

import pydantic
import requests

from registrations.domain.hospital import registration
from registrations.domain.repo.registration_repo import InterfaceHospitalRepo
from registrations.infrastructure.adapters.repos.postgres_m3o import m3o_dto


M3O_DB_LOGGER = logging.getLogger(__name__)

error_stream_handler = logging.StreamHandler(stream=sys.stderr)
error_stream_handler.setLevel(logging.CRITICAL)

log_handlers = logging.StreamHandler(stream=sys.stdout)
log_handlers.setLevel(logging.INFO)

M3O_DB_LOGGER.addHandler(error_stream_handler)
M3O_DB_LOGGER.addHandler(log_handlers)

M3O_API_TOKEN = os.getenv("M3O_API_TOKEN")


class M3OHospitalRepoImpl(InterfaceHospitalRepo):
    def __init__(self) -> None:
        self.__session_api = M3O_API_TOKEN
        self.__unverified_tbl = "unverified_hospital"
        self.__unclaimed_hospital = "unclaimed_hospital"
        self.pending_transaction: list[Callable] = []

    async def save_unverified_hospital(
        self, **kwargs: registration.HospitalEntryDictType
    ) -> registration.UnverifiedRegisteredHospital:
        try:
            # check if unverified hospital exists then return exists error.
            if self._record_exists(self.__unverified_tbl, **kwargs):
                raise Exception("raise a real error")
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
                raise Exception("raise a real error")
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

    def set_executable(self) -> None:
        for each_callable_transaction in self.pending_transaction:
            each_callable_transaction()

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
