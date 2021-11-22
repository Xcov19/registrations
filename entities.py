import datetime

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


class HealthCareEntity(pyd.BaseModel):
    name: str
    registration_number: str
    incorporation_date: datetime.date
    registering_user_info: RegisteringUser
    location: Location
    icu_beds: int = None
    non_icu_beds: int = None
    ventilator_beds: int = None
    non_ventilator_beds: int = None
    num_departments: int = None
    hospital_contact_number: str
    is_verified: bool = Field(default=False)


class HealthCareRecordEntity(HealthCareEntity):
    """Orm mappable healthcare data that fetches from database."""

    id: int
    registering_user_info: ClericalRegisteredRecord
    location: LocationRecord

    class Config:
        orm_mode = True
