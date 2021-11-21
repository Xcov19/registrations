"""Although initial motivation was to build this app service around
beanie, motor and async mongo operations, with **supabase** offering
firebase like service built around postgresql, i've shifted to using postgresql.
This in no way hinders the possibility, by design, of using beanie and mongo.
Switching to MongoRepo as the adapter port is possible
with the same use case but in a different db context while abstracting away
how it is used internally."""
from __future__ import annotations

import functools
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

import anyio
import beanie
import orm
import sqlalchemy as sa
from motor import motor_asyncio

import models
from entities import HealthCareRecordEntity
from interfaces import MongoRepoInterface
from interfaces import SqlRepoInterface
from models import HealthCareData
from settings import DB_CONNECTION


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
        import asyncio

        # Probably a fix.
        # See: https://github.com/encode/orm/issues/114#issuecomment-974735799
        url = self.model._get_database_url()
        await asyncio.gather(asyncio.create_task(self.model._create_all(url)))


async def start_psql_client(model_registry: orm.ModelRegistry):
    await PsqlClient(model_registry).create_async_model()


def get_postgres_collections(
    collections: List[str], models_registry: orm.ModelRegistry
) -> Dict[str, orm.Model]:
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
    required_registration_fields = (
        "registration_number",
        "name",
        "location",
    )
    # Returns table name with their orm models.
    collection_mapping = get_postgres_collections(
        [
            healthcare_tbl_name,
            location_tbl_name,
            clerical_tbl_name,
        ],
        models_registry,
    )

    @classmethod
    def get_healthcare_table(cls, **tbl_mapping) -> orm.Model:
        """Gets orm table model for healthcare data."""
        return tbl_mapping[cls.healthcare_tbl_name]

    @classmethod
    async def validate_entry(cls, **kwargs) -> bool:
        """Validates if record doesn't exist."""
        orm_model = cls.get_healthcare_table(**cls.collection_mapping)
        return bool(orm_model and not await orm_model.objects.first(**kwargs))

    @classmethod
    async def is_duplicate(cls, **kwargs) -> bool:
        """Checks if it is a duplicate entry."""
        orm_model = cls.get_healthcare_table(**cls.collection_mapping)
        return bool(orm_model and await orm_model.objects.first(**kwargs))

    @classmethod
    async def create_object(cls, **kwargs) -> HealthCareRecordEntity:
        orm_model = cls.get_healthcare_table(**cls.collection_mapping)
        new_record = orm_model.objects.create(**kwargs)
        return HealthCareRecordEntity.from_orm(new_record)


class MotorClient(Borg):
    """Creates a singleton motor client instance."""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            cls.__instance.client = motor_asyncio.AsyncIOMotorClient(DB_CONNECTION)
        return cls.__instance

    @functools.cached_property
    def motor_client(self) -> motor_asyncio.AsyncIOMotorClient:
        return self.__instance.client

    async def start_mongo_collection(
        self, collections: list
    ) -> motor_asyncio.AsyncIOMotorClient:
        # Init beanie
        await beanie.init_beanie(
            database=self.motor_client.db_name, document_models=collections
        )
        return self.motor_client


class MongoRepo(MongoRepoInterface):
    """Repo for registrations data in mongodb."""

    healthcare_collection = models.HealthCareData
    client = MotorClient().start_mongo_collection([healthcare_collection])

    @classmethod
    def get_healthcare_collection(cls) -> Type[HealthCareData]:
        """Returns healthcare mongo model."""
        return cls.healthcare_collection

    @classmethod
    async def validate_entry(cls, **search_criteria) -> bool:
        """Validates if document doesn't exist."""
        collection = cls.get_healthcare_collection()
        return not bool(await collection.find_one(**search_criteria))

    @classmethod
    async def is_duplicate(cls, **search_criteria) -> bool:
        """Checks if constraints already fetch an existing document."""
        collection = cls.get_healthcare_collection()
        return bool(await collection.find_one(**search_criteria))

    @classmethod
    async def create_object(cls, **kwargs) -> HealthCareRecordEntity:
        collection = cls.get_healthcare_collection()
        document = collection(**kwargs)
        new_record = await HealthCareData.insert_one(document)
        return HealthCareRecordEntity(**{**kwargs, id: new_record.inserted_id})
