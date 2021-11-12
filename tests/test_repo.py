import unittest

import pytest

from interfaces import MongoRepoInterface
from repo import Singleton


class StubClient(Singleton):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance


@pytest.fixture(autouse=True)
def motor_client_stub():
    return StubClient()


class MongoRepo(MongoRepoInterface):
    @classmethod
    def init(cls):
        return StubClient()

    @classmethod
    async def get_collection(cls, collections: list):
        motor_client_stub = cls.init()
        yield motor_client_stub


class TestRepo(unittest.TestCase):
    ...
