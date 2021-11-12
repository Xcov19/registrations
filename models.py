import datetime
from typing import Optional

import beanie
import databases
import orm
import pymongo
from pymongo import IndexModel

import settings
from entities import Location
from entities import RegisteringUser

database = databases.Database(settings.DB_CONNECTION.get("postgres"))
models = orm.ModelRegistry(database=database)


class ClericalRegisteredData(orm.Model):
    registry = models
    tablename = "clerical_registered_data"
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=False),
        "name": orm.String(allow_null=False, allow_blank=False),
        "title": orm.String(allow_null=False, allow_blank=False),
        "contact_number": orm.String(allow_null=False, allow_blank=False),
    }


class LocationData(orm.Model):
    registry = models
    tablename = "location"
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=False),
        "lat": orm.Decimal(decimal_places=5, max_digits=4),
        "lng": orm.Decimal(decimal_places=5, max_digits=4),
        "city": orm.String(allow_null=False, allow_blank=False),
        "state": orm.String(allow_null=False, allow_blank=False),
        "country": orm.String(allow_null=False, allow_blank=False),
    }


class HealthCare(orm.Model):
    registry = models
    tablename = "healthcare_registration"
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=False),
        "name": orm.String(allow_null=False, allow_blank=False),
        "registration_number": orm.String(allow_null=False, allow_blank=False),
        "incorporation_date": orm.Date(allow_null=False, allow_blank=False),
        "registering_user_info": orm.ForeignKey(ClericalRegisteredData),
        "location": orm.ForeignKey(LocationData),
        "icu_beds": orm.Integer(allow_null=True),
        "non_icu_beds": orm.Integer(allow_null=True),
        "ventilator_beds": orm.Integer(allow_null=True),
        "non_ventilator_beds": orm.Integer(allow_null=True),
        "num_departments": orm.Integer(allow_null=True),
        "hospital_contact_number": orm.String(allow_null=False, allow_blank=False),
    }


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
