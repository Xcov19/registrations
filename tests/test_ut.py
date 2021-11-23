import datetime as dt
import unittest

import pytest

from entities import HealthCareEntity
from entities import HealthCareRecordEntity
from entities import Location
from entities import RegisteringUser
from interfaces import SqlRepoInterface
from repo import Borg
from use_case import HospitalRegistrationUseCase
from use_case import register_use_case


# TODO: mongo client testing
class MongoStubClient(Borg):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance


@pytest.fixture(autouse=True)
def motor_client_stub():
    return MongoStubClient()


# @unittest.skip("Not implementing Mongo driver for now.")
# class MongoRepo(MongoRepoInterface):
#     @classmethod
#     def init(cls):
#         return MongoStubClient()
#
#     @classmethod
#     async def get_collection(cls, collections: list):
#         motor_client_stub = cls.init()
#         yield motor_client_stub


class ObjectManagerStub:
    def __init__(self):
        self.__instance = None
        self.__owner = None

    @property
    def instance(self):
        return self.__instance, self.__owner

    def __get__(self, instance, owner):
        if not self.__instance:
            self.__instance = instance
            self.__owner = owner
        return self

    @staticmethod
    def create(**kwargs):
        return HealthCareRecordEntity(**{**kwargs, id: 1})

    @staticmethod
    def first(**kwargs):
        return HealthCareRecordEntity(**{**kwargs, id: 1})


class HealthCareTableStub:
    """A table stub that imitates real model.

    The idea is to quack like a duck and follow the interface without mocking.
    Delegates expected object methods to another stub to be used in PsqlRepoStub
    to imitate real model behaviour.
    """

    objects = ObjectManagerStub()


class PsqlRepoStub(SqlRepoInterface):
    healthcare_tbl_name = "healthcare"
    location_tbl_name = "location"
    clerical_tbl_name = "clerical_user"
    # Returns table name with their orm models.
    collection_mapping = {
        healthcare_tbl_name: HealthCareTableStub,
    }

    @classmethod
    def get_healthcare_table(cls, **tbl_mapping):
        return tbl_mapping.get(cls.healthcare_tbl_name)

    @classmethod
    async def validate_entry(cls, **kwargs) -> bool:
        return True

    @classmethod
    async def is_duplicate(cls, **kwargs) -> bool:
        return bool(HealthCareTableStub.objects.first(**kwargs))

    @classmethod
    async def create_object(cls, **kwargs) -> HealthCareRecordEntity:
        return HealthCareTableStub.objects.create(**kwargs)


class TestHospitalRegistrationUseCase(unittest.TestCase):
    """Testing service and business logic."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.healthcare_data = HealthCareEntity(
            name="a covid hospital",
            registration_number="COVXYZ123",
            incorporation_date=dt.date(2021, 11, 18),
            registering_user_info=RegisteringUser(
                name="A clerical name",
                title="A clerical title",
                contact_number="0083819774694",
            ),
            location=Location(
                lat=56.45,
                lng=43.56,
                city="paradise city",
                state="Paradi Estate",
                country="Tagadella",
            ),
            hospital_contact_number="0083819774694",
        )

    def setUp(self):
        self.repo = PsqlRepoStub
        self.adapter = HospitalRegistrationUseCase
        self.use_case = register_use_case(self.adapter, self.repo)

    @pytest.mark.anyio
    async def test_valid_registration_data(self):
        expected = await self.use_case.valid_new_entry(self.healthcare_data)
        self.assertTrue(expected, "Should be valid")

    @pytest.mark.anyio
    async def test_duplicate_registration_exists(self):
        expected = await self.use_case.duplicate_exists(self.healthcare_data)
        self.assertFalse(expected, "There should be no duplicate")

    @pytest.mark.anyio
    async def test_register_data(self):
        expected = await self.use_case.create_entry(self.healthcare_data)
        self.assertTrue(expected, "Should be created")
        self.assertIsInstance(expected, HealthCareRecordEntity)
