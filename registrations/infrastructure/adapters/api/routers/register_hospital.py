from typing import Optional

import fastapi

from registrations.domain.dto import HospitalRegistrationEntry
from registrations.domain.dto import RegisterKeyContact

router = fastapi.APIRouter(
    tags=["hospitals", "registration"],
)


@router.post(
    "/register-hospital",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=HospitalRegistrationEntry,
)
async def register_hospital_center(
    healthcare_data: HospitalRegistrationEntry,
    q: Optional[dict[str, str]] = None,
):
    # TODO: pass this into HospitalRegistrationApplicationService
    #  post dependency injection
    if q and (verified_status := q.get("verified_status")):
        healthcare_data.verified_status = verified_status
    elif q and (key_contact := q.get("key_contact")):
        healthcare_data.key_contact = RegisterKeyContact(**q)
    return healthcare_data
