"""Implements interfaces to various layered-components.
See motivation behind interfaces and brief guide:
https://www.godaddy.com/engineering/2018/12/20/python-metaclasses/
"""
import abc
from typing import AsyncGenerator
from typing import Dict
from typing import Protocol
from typing import Type
from typing import TypeVar
from typing import Union

import beanie
import orm


class RepoInterface(Protocol):
    """Generic repository interface."""

    @classmethod
    @abc.abstractmethod
    def collection_mapping(cls) -> Dict[str, orm.Model]:
        """Maps models for each repo operations"""
        ...

    @classmethod
    @abc.abstractmethod
    def get_healthcare_table(cls, **tbl_mapping):
        ...

    @classmethod
    @abc.abstractmethod
    async def validate_entry(
        cls, model_collection: Union[beanie.Document, orm.Model], /, **kwargs
    ) -> bool:
        """Validates whether given object is valid for repo processing."""
        ...

    @classmethod
    @abc.abstractmethod
    async def is_duplicate(
        cls, model_collection: Union[beanie.Document, orm.Model], /, **kwargs
    ) -> bool:
        """Checks if it's a duplicate object."""
        ...

    @classmethod
    @abc.abstractmethod
    async def create_object(
        cls, model_collection: Union[Type[beanie.Document], orm.Model], /, **kwargs
    ):
        """Creates a new entry from the given object."""
        ...


class SqlRepoInterface(RepoInterface, Protocol):
    """Sql DB interface for rdbms drivers."""

    healthcare_tbl_name: str
    location_tbl_name: str
    clerical_tbl_name: str
    models_registry: orm.ModelRegistry


class MongoRepoInterface(RepoInterface, Protocol):
    """Mongo interface for mongo repo drivers."""

    @classmethod
    @abc.abstractmethod
    async def get_collection(cls, collections: list):
        ...
