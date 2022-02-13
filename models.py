import asyncio
import datetime
from typing import Dict
from typing import Optional

import beanie
import databases
import orm
import pymongo
from pymongo import IndexModel

import settings
from entities import Location
from entities import RegisteringUser

database = databases.Database(settings.ENV_CLASS.postgres_uri)
models = orm.ModelRegistry(database=database)


class ClericalRegisteredData(orm.Model):
    registry = models
    tablename = "clerical_registered_data"
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=False),
        "name": orm.String(allow_null=False, allow_blank=False, max_length=128),
        "title": orm.String(allow_null=False, allow_blank=False, max_length=128),
        "contact_number": orm.String(
            allow_null=False, allow_blank=False, max_length=14
        ),
    }


class LocationData(orm.Model):
    registry = models
    tablename = "location"
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=False),
        "lat": orm.Decimal(decimal_places=5, max_digits=5),
        "lng": orm.Decimal(decimal_places=5, max_digits=5),
        "city": orm.String(allow_null=False, allow_blank=False, max_length=50),
        "state": orm.String(allow_null=False, allow_blank=False, max_length=50),
        "country": orm.String(allow_null=False, allow_blank=False, max_length=3),
    }


class HealthCare(orm.Model):
    registry = models
    tablename = "healthcare_registration"
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=False),
        "name": orm.String(allow_null=False, allow_blank=False, max_length=200),
        "registration_number": orm.String(
            allow_null=False, allow_blank=False, max_length=200
        ),
        "incorporation_date": orm.Date(allow_null=False, allow_blank=False),
        "registering_user_info": orm.ForeignKey(
            ClericalRegisteredData, on_delete=orm.CASCADE
        ),
        "location": orm.ForeignKey(LocationData, on_delete=orm.CASCADE),
        "icu_beds": orm.Integer(allow_null=True),
        "non_icu_beds": orm.Integer(allow_null=True),
        "ventilator_beds": orm.Integer(allow_null=True),
        "non_ventilator_beds": orm.Integer(allow_null=True),
        "num_departments": orm.Integer(allow_null=True),
        "hospital_contact_number": orm.String(
            allow_null=False, allow_blank=False, max_length=14
        ),
        "is_verified": orm.Boolean(allow_null=False, default=False),
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
    is_verified: bool

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


class Borg:
    """Borg inspired singleton class."""

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class PsqlClient(Borg):
    """Creates a singleton postgresql client instance.

    This creates all postgres tables for a database only once.
    To be used during startup event of a asgi server or
    with dependency injection.
    """

    __instance: Optional[Borg] = None

    def __new__(cls, model: orm.ModelRegistry, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, model: orm.ModelRegistry):
        super().__init__()
        self.model = model

    async def create_async_model(self):

        url = self.model._get_database_url()
        tasks = [
            # See: https://github.com/encode/databases/issues/96#issuecomment-619425993
            asyncio.create_task(self.model.database.connect()),
            # Probably a fix.
            # See: https://github.com/encode/orm/issues/114#issuecomment-974735799
            asyncio.create_task(self.model._create_all(url)),
        ]
        await asyncio.gather(*tasks)

    async def drop_async_model(self):
        url = self.model._get_database_url()
        await self.model._drop_all(url)
        await self.model.database.disconnect()


async def start_psql_client(model_registry: orm.ModelRegistry):
    await PsqlClient(model_registry).create_async_model()


async def drop_psql_client(model_registry: orm.ModelRegistry):
    await PsqlClient(model_registry).drop_async_model()


def get_postgres_collections(
    models_registry: orm.ModelRegistry,
) -> Dict[str, orm.Model]:
    """Returns a dictionary of collection name with orm object."""
    tables: Dict[str, orm.ModelRegistry] = models_registry.models
    return {
        orm_registry_model.tablename: orm_registry_model
        for orm_registry_model in tables.values()
    }
