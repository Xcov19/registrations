import logging
import random
import uuid
from typing import Any

import pytest
from pytest import FixtureRequest

from registrations.domain import dto
from registrations.domain.hospital.registration import (
    ContactPerson,
    OwnershipType,
    PhoneNumber,
    VerificationStatus,
)
from registrations.domain.location import location
from registrations.domain.location.location import Address


# ************************************************* #
# Setup pytest anyio fixture.
# The anyio_backend fixture determines the backends
# and their options that tests and fixtures are run with.
# The AnyIO pytest plugin comes with a function scoped
# fixture with this name which runs everything on all supported backends.
# ************************************************* #
@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request: FixtureRequest.session) -> Any:  # type: ignore[no-any-unimported]
    return request.param


# ************************************************* #
# Setup a fixture caplog for unsuccessful tests.
# You can run pytest -ra -q to see only unsuccessful logs.
# ************************************************* #
@pytest.fixture(scope="function", autouse=True)
def caplogger(caplog: Any) -> Any:
    caplog.set_level(logging.ERROR, logger="tests.test_registrations")
    return caplog


@pytest.fixture(scope="module")
def generate_uuid1() -> uuid.UUID:
    random.seed(13)
    return uuid.uuid1(random.randint(1, 13))


@pytest.fixture
def hospital_root(generate_uuid1: uuid.UUID) -> dict:
    return {
        "hospital_id": generate_uuid1,
        "hospital_name": "Rajajayah Paramvir",
        "ownership_type": OwnershipType.Pub_Pvt,
        "address": Address(
            street="Rajaji marg", city="Newark", state="MP", country="IN"
        ),
        "phone_number": PhoneNumber(number="+919425411234"),
    }


@pytest.fixture
def valid_unverified_hospital(hospital_root: dict) -> dict:
    return {
        **hospital_root,
        **{
            "key_contact_registrar": ContactPerson(
                name="Radhe Shyam",
                mobile_number=PhoneNumber(number="+919425411234"),
            ),
        },
    }


@pytest.fixture
def invalid_unverified_hospital(hospital_root: dict) -> dict:
    return hospital_root


@pytest.fixture
def valid_unclaimed_hospital(hospital_root: dict) -> dict:
    return {
        **hospital_root,
        **{
            "verified_status": VerificationStatus.Verified,
        },
    }


@pytest.fixture
def invalid_unclaimed_hospital(hospital_root: dict) -> dict:
    return {
        **hospital_root,
        **{
            "verified_status": False,
        },
    }


@pytest.fixture(scope="class")
def registration_entry_manual_verification() -> dto.ToHospitalRegistrationEntry:
    return dto.ToHospitalRegistrationEntry(
        name="A hospital",
        ownership_type="public",
        hospital_contact_number="+919425411234",
        verified_status="unverified",
        key_contact=dto.RegisterKeyContact(name="Radhe Shyam", mobile="+919425416789"),
        address=location.Address(
            street="Rajaji marg", city="Newark", state="MP", country="IN"
        ),
        added_since="2022-01-01T00:00:00Z",
    )


@pytest.fixture(scope="class")
def registration_entry_unclaimed() -> dto.ToHospitalRegistrationEntry:
    return dto.ToHospitalRegistrationEntry(
        name="A Private hospital",
        ownership_type="private",
        hospital_contact_number="+919425411234",
        verified_status="verified",
        address=location.Address(
            street="Rajaji marg", city="Newark", state="MP", country="IN"
        ),
    )
