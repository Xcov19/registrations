"""Although initial motivation was to build this app service around
beanie, motor and async mongo operations, with **supabase** offering
firebase like service built around postgresql, i've shifted to using postgresql.
This in no way hinders the possibility, by design, of using beanie and mongo.
Switching to MongoRepo as the adapter port is possible
with the same use case but in a different db context while abstracting away
how it is used internally."""
from __future__ import annotations

import functools
from typing import Type

import beanie
import models
import orm
from entities import HealthCareRecordEntity
from interfaces import MongoRepoInterface, SqlRepoInterface
from models import HealthCareData
from motor import motor_asyncio

import settings


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
    collection_mapping = models.get_postgres_collections(
        models_registry,
    )

    @classmethod
    def get_healthcare_table(cls, **tbl_mapping) -> orm.Model:
        """Gets orm table model for healthcare data."""
        return tbl_mapping[cls.healthcare_tbl_name]

    @classmethod
    def get_location_table(cls, **tbl_mapping):
        """Returns location sql table."""
        return tbl_mapping[cls.location_tbl_name]

    @classmethod
    def get_clerical_table(cls, **tbl_mapping):
        """Returns clerical user sql table."""
        return tbl_mapping[cls.clerical_tbl_name]

    @classmethod
    async def validate_entry(cls, **kwargs) -> bool:
        """Validates if record doesn't exist."""
        kwargs.pop("location", None)
        kwargs.pop("registering_user_info", None)
        orm_model = cls.get_healthcare_table(**cls.collection_mapping)
        await cls.models_registry.database.connect()
        return bool(orm_model and not await orm_model.objects.first(**kwargs))

    @classmethod
    async def is_duplicate(cls, **kwargs) -> bool:
        """Checks if it is a duplicate entry."""
        kwargs.pop("location", None)
        kwargs.pop("registering_user_info", None)
        orm_model = cls.get_healthcare_table(**cls.collection_mapping)
        await cls.models_registry.database.connect()
        return bool(orm_model and await orm_model.objects.first(**kwargs))

    @classmethod
    async def create_object(cls, **kwargs) -> HealthCareRecordEntity:
        location = kwargs.pop("location")
        registering_user_info = kwargs.pop("registering_user_info")
        orm_healthcare = cls.get_healthcare_table(**cls.collection_mapping)
        orm_location = cls.get_location_table(**cls.collection_mapping)
        orm_clerical = cls.get_clerical_table(**cls.collection_mapping)
        await cls.models_registry.database.connect()
        location_record = await orm_location.objects.create(**location)
        clerical_record = await orm_clerical.objects.create(**registering_user_info)
        new_record = await orm_healthcare.objects.create(
            **{
                **kwargs,
                "location": location_record,
                "registering_user_info": clerical_record,
            }
        )
        new_record = await orm_healthcare.objects.select_related(
            [
                "registering_user_info",
                "location",
            ]
        ).get(id=new_record.id)
        return HealthCareRecordEntity.from_orm(new_record)


class MotorClient(models.Borg):
    """Creates a singleton motor client instance."""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            cls.__instance.client = motor_asyncio.AsyncIOMotorClient(
                settings.ENV_CLASS.mongo_uri
            )
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
