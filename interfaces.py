"""Implements interfaces to various layered-components.
See motivation behind interfaces and brief guide:
https://www.godaddy.com/engineering/2018/12/20/python-metaclasses/
"""
import abc
from typing import Dict
from typing import Protocol
from typing import Type

import beanie
import orm

from entities import HealthCareRecordEntity
from models import HealthCareData


class RepoInterface(Protocol):
    """Generic repository interface."""

    @classmethod
    @abc.abstractmethod
    async def validate_entry(cls, **kwargs) -> bool:
        """Validates whether given object is valid for repo processing."""
        ...

    @classmethod
    @abc.abstractmethod
    async def is_duplicate(cls, **kwargs) -> bool:
        """Checks if it's a duplicate object."""
        ...

    @classmethod
    @abc.abstractmethod
    async def create_object(cls, **kwargs) -> HealthCareRecordEntity:
        """Creates a new entry from the given object."""
        ...


class SqlRepoInterface(RepoInterface, Protocol):
    """Sql DB interface for rdbms drivers."""

    healthcare_tbl_name: str
    location_tbl_name: str
    clerical_tbl_name: str
    models_registry: orm.ModelRegistry
    required_registration_fields: tuple
    collection_mapping: dict

    @classmethod
    @abc.abstractmethod
    def get_healthcare_table(cls, **tbl_mapping):
        """Returns healthcare sql table."""
        ...

    @classmethod
    @abc.abstractmethod
    def get_location_table(cls, **tbl_mapping):
        """Returns location sql table."""
        ...

    @classmethod
    @abc.abstractmethod
    def get_clerical_table(cls, **tbl_mapping):
        """Returns clerical user sql table."""
        ...


class MongoRepoInterface(RepoInterface, Protocol):
    """Mongo interface for mongo repo drivers."""

    healthcare_collection: Type[beanie.Document]

    @classmethod
    @abc.abstractmethod
    def get_healthcare_collection(cls) -> Type[HealthCareData]:
        """Returns healthcare sql table."""
        ...
