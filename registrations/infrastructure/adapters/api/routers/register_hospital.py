from __future__ import annotations

from typing import Optional

import fastapi

from registrations.domain.dto import (
    RegisterKeyContact,
    ToHospitalRegistrationEntry,
)

router = fastapi.APIRouter(
    tags=["hospitals", "registration"],
)


@router.post(
    "/register-hospital",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=ToHospitalRegistrationEntry,
)
async def register_hospital_center(
    healthcare_data: ToHospitalRegistrationEntry,
    q: Optional[dict] = None,
):
    # TODO: pass this into HospitalRegistrationApplicationService
    #  post dependency injection
    if q and (verified_status := q.get("verified_status")):
        healthcare_data.verified_status = verified_status
    elif (
        isinstance(q, dict)
        and q.keys() == RegisterKeyContact.schema()["properties"].keys()
    ):
        healthcare_data.key_contact = RegisterKeyContact(**q)
    return healthcare_data
