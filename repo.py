"""Although initial motivation was to build this app service around
beanie, motor and async mongo operations, with **supabase** offering
firebase like service built around postgresql, i've shifted to using postgresql.
This in no way hinders the possibility, by design, of using beanie and mongo.
Switching to MongoRepo as the adapter port is possible
with the same use case but in a different db context while abstracting away
how it is used internally."""
from __future__ import annotations

import functools
from typing import Any
from typing import AsyncGenerator
from typing import Coroutine
from typing import Dict
from typing import List
from typing import Type
from typing import Union

import beanie
import motor
import orm
import sqlalchemy as sa
from pymongo.results import InsertOneResult

import models
from interfaces import MongoRepoInterface
from interfaces import SqlRepoInterface
from interfaces import Type_R
from models import HealthCareData
from settings import DB_CONNECTION

ORM_MAP_T = Dict[str, orm.Model]


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

    __instance: Borg

    def __new__(cls, model: orm.ModelRegistry, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            model.create_all()
        return cls.__instance

    def __init__(self, model: orm.ModelRegistry):
        super().__init__()
        self.model = model

    @classmethod
    def client_model(cls) -> Union[None, models.models]:
        """Returns the registered orm model registry from a database."""
        return cls.__instance and cls.__instance.client


def start_psql_client() -> PsqlClient:
    return PsqlClient(models.models)


@functools.lru_cache
def get_postgres_collections(
    collections: List[str], models_registry: orm.ModelRegistry
) -> ORM_MAP_T:
    """Returns a dictionary of collection name with orm object."""
    tables: Dict[str, sa.Table] = models_registry.metadata.tables
    return {
        tbl_name: models_registry.models.get(tbl_name)
        for tbl_name in collections
        if tbl_name in tables
    }


class PsqlRepo(SqlRepoInterface):
    """Repo for registrations data in postgresql."""

    healthcare_tbl_name = models.HealthCare.tablename
    location_tbl_name = models.LocationData.tablename
    clerical_tbl_name = models.ClericalRegisteredData.tablename
    models_registry = models.models

    @classmethod
    def collection_mapping(cls) -> ORM_MAP_T:
        """Returns table name with their orm models."""
        return get_postgres_collections(
            [
                cls.healthcare_tbl_name,
                cls.location_tbl_name,
                cls.clerical_tbl_name,
            ],
            cls.models_registry,
        )

    @classmethod
    def get_healthcare_table(cls, **tbl_mapping) -> orm.Model:
        return tbl_mapping[cls.healthcare_tbl_name]

    @classmethod
    async def validate_entry(cls, orm_model: orm.Model, /, **kwargs) -> bool:
        """Validates if record doesn't exist."""
        return bool(orm_model) and not (await orm_model.objects.first(**kwargs))

    @classmethod
    async def is_duplicate(cls, orm_model: orm.Model, /, **kwargs) -> bool:
        # TODO: implement
        ...

    @classmethod
    async def create_object(cls, orm_model: orm.Model, /, **kwargs):
        # TODO: implement
        ...


class MotorClient(Borg):
    """Creates a singleton motor client instance."""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            cls.__instance.client = motor.motor_asyncio.AsyncIOMotorClient(
                DB_CONNECTION
            )
        return cls.__instance

    def motor_client(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        return self.__instance.client


# TODO: populate logic with motor and
#  implement collection_mapping
class MongoRepo(MongoRepoInterface):
    @classmethod
    def init(cls):
        """Initializes singleton motor client."""
        return MotorClient().motor_client()

    @classmethod
    async def get_collection(cls, collections: list):
        motor_client = cls.init()
        # Init beanie
        await beanie.init_beanie(
            database=motor_client.db_name, document_models=collections
        )
        return motor_client

    @classmethod
    async def validate_entry(
        cls, collection: beanie.Document, /, **search_criteria
    ) -> bool:
        """Validates if document doesn't exist."""
        return not bool(await collection.find_one(search_criteria))

    @classmethod
    async def is_duplicate(
        cls, collection: beanie.Document, /, **search_criteria
    ) -> bool:
        """Checks if constraints already fetch an existing document."""
        return bool(await collection.find_one(search_criteria))

    @classmethod
    async def create_object(
        cls, collection: Type[beanie.Document], /, **kwargs
    ) -> Coroutine[Any, Any, InsertOneResult]:
        document = collection(**kwargs)
        return HealthCareData.insert_one(document)
