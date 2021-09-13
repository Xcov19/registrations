from __future__ import annotations

from typing import List
from typing import Type
from typing import Union

import beanie
import motor

from interfaces import IRepo
from models import HealthCareData
from settings import DB_CONNECTION


class Singleton:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class MotorClient(Singleton):
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


# TODO: populate logic with motor
class MongoRepo(IRepo):
    @classmethod
    def init(cls):
        """Initializes singleton motor client."""
        return MotorClient().motor_client()

    @classmethod
    async def get_collection(cls, collections: List[Union[str, Type[beanie.Document]]]):
        motor_client = cls.init()
        # Init beanie
        await beanie.init_beanie(
            database=motor_client.db_name, document_models=collections
        )
        yield motor_client

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
    async def create_object(cls, collection: Type[beanie.Document], /, **kwargs):
        document = collection(**kwargs)
        await HealthCareData.insert_one(document)
