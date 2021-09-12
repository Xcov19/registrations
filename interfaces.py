import abc
import functools

import beanie

from models import HealthCareData


class IRepo(metaclass=abc.ABCMeta):

    impl_methods = (
        "validate_entry",
        "is_duplicate",
        "create_object",
    )

    @staticmethod
    def get_impl(subclass: object, method_name: str) -> bool:
        return hasattr(subclass, method_name)

    @classmethod
    def __subclasshook__(cls, subclass):
        impl_fn = functools.partial(cls.get_impl, subclass)
        return all(map(impl_fn, cls.impl_methods))

    @classmethod
    @abc.abstractmethod
    async def get_collection(cls, collections: list):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def validate_entry(cls, collection: beanie.Document, /, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def is_duplicate(cls, collection: beanie.Document, /, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def create_object(cls, collection, /, **kwargs):
        raise NotImplementedError
