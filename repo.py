from __future__ import annotations

from entities import NewHealthCareData
from interfaces import IRepo


# TODO: populate logic with motor
class MongoRepo(IRepo):
    @classmethod
    def validate_entry(cls, **kwargs) -> bool:
        ...

    @classmethod
    def is_duplicate(cls, **kwargs) -> bool:
        ...

    @classmethod
    async def create_object(cls, **kwargs) -> NewHealthCareData:
        ...
