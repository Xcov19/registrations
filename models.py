import datetime
from typing import Optional

import beanie
import pymongo
from pymongo import IndexModel

from entities import Location
from entities import RegisteringUser


class HealthCareData(beanie.Document):
    name: str
    registration_number: str
    incorporation_date: datetime.datetime
    registering_user_info: RegisteringUser
    location: Location
    icu_beds: Optional[int]
    non_icu_beds: Optional[int]
    ventilator_beds: Optional[int]
    non_ventilator_beds: Optional[int]
    num_departments: int
    hospital_contact_number: str

    class Collection:
        name = "health_centers"
        indexes = [
            "name",
            IndexModel(
                [
                    ("incorporation_date", pymongo.ASCENDING),
                ]
            ),
        ]
