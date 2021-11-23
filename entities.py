import datetime
from typing import Optional

import pydantic as pyd
from pydantic import Field


class Location(pyd.BaseModel):
    lat: float
    lng: float
    city: str
    state: str
    country: str


class LocationRecord(Location):
    """Orm mappable Location record that fetches from database."""

    id: int

    class Config:
        orm_mode = True


class RegisteringUser(pyd.BaseModel):
    name: str
    title: str
    contact_number: str


class ClericalRegisteredRecord(RegisteringUser):
    """Orm mappable Clerical Registration record that fetches from database."""

    id: int

    class Config:
        orm_mode = True


class HospitalOnlyEntity(pyd.BaseModel):
    name: str
    registration_number: str
    incorporation_date: datetime.date
    icu_beds: Optional[int]
    non_icu_beds: Optional[int]
    ventilator_beds: Optional[int]
    non_ventilator_beds: Optional[int]
    num_departments: Optional[int]
    hospital_contact_number: str
    is_verified: bool = Field(default=False)


class HealthCareEntity(HospitalOnlyEntity):
    """Read only healthcare entity."""

    registering_user_info: RegisteringUser
    location: Location


class HealthCareRecordEntity(HospitalOnlyEntity):
    """Orm mappable healthcare data that fetches from database."""

    id: int
    registering_user_info: ClericalRegisteredRecord
    location: LocationRecord

    class Config:
        orm_mode = True
