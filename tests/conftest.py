import random
import uuid

import pytest

from registrations.domain.hospital.registration import ContactPerson
from registrations.domain.hospital.registration import OwnershipType
from registrations.domain.hospital.registration import PhoneNumber
from registrations.domain.hospital.registration import VerificationStatus
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
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="module")
def generate_uuid1():
    random.seed(13)
    return uuid.uuid1(random.randint(1, 13))


@pytest.fixture
def hospital_root(generate_uuid1: uuid.uuid1) -> dict:
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
            )
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
