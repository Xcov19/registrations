import abc
import functools
from typing import Union

from entities import NewHealthCareData


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
    def __subclasshook__(cls, subclass) -> Union[bool, NotImplemented]:
        impl_fn = functools.partial(cls.get_impl, subclass)
        return all(map(impl_fn, cls.impl_methods))

    @classmethod
    @abc.abstractmethod
    def validate_entry(cls, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def is_duplicate(cls, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create_object(cls, **kwargs) -> NewHealthCareData:
        raise NotImplementedError
