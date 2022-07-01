"""Data transfer object for domain registration."""
from __future__ import annotations

from typing import Optional

import pydantic

from registrations.domain.location.location import Address


class RegisterKeyContact(
    pydantic.BaseModel,
    allow_mutation=False,
    validate_assignment=True,
    arbitrary_types_allowed=False,
):
    """Key contact person registering hospital."""

    name: str
    mobile: str
    email: Optional[pydantic.EmailStr]


class HospitalRegistrationEntry(
    pydantic.BaseModel,
    allow_mutation=False,
    validate_assignment=True,
    arbitrary_types_allowed=False,
):
    """Hospital registration details."""

    name: str
    ownership_type: str
    hospital_contact_number: str
    key_contact: Optional[RegisterKeyContact]
    verified_status: Optional[str]
    address: Address
