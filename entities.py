import datetime

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lng: float
    city: str
    state: str
    country: str


class RegisteringUser(BaseModel):
    name: str
    title: str
    contact_number: str


class HealthCareData(BaseModel):
    name: str
    registration_number: str
    incorporation_date: datetime.datetime
    registering_user_info: RegisteringUser
    location: Location
    icu_beds: int
    non_icu_beds: int
    ventilator_beds: int
    non_ventilator_beds: int
    num_departments: int
    hospital_contact_number: str


class NewHealthCareData(HealthCareData):
    id: str
