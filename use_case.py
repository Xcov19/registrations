import functools
from typing import Callable
from typing import Dict
from typing import Type
from typing import Union

import orm

import models
from models import HealthCareData
from repo import MongoRepo
from repo import PsqlRepo


@functools.lru_cache
def register_use_case(use_case_callable: Callable, repo_callable: Callable):
    return use_case_callable(repo_callable)


class HospitalRegistrationUseCase:
    def __init__(self, repo: Union[Type[PsqlRepo], Type[MongoRepo]]):
        self.__repo = repo
        self.__tbl_map = {}

    @functools.cached_property
    def collections_map(self) -> Dict[str, orm.Model]:
        if not self.__tbl_map:
            self.__tbl_map: Dict[str, orm.Model] = self.__repo.collection_mapping()
        return self.__tbl_map

    async def valid_new_entry(self, healthcare_data: HealthCareData) -> bool:
        orm_model = self.__repo.get_healthcare_table(**self.collections_map)
        return await self.__repo.validate_entry(orm_model, **healthcare_data.dict())

    async def duplicate_exists(self, healthcare_data: HealthCareData) -> bool:
        orm_model = self.__repo.get_healthcare_table(**self.collections_map)
        return await self.__repo.is_duplicate(orm_model, **healthcare_data.dict())

    async def create_entry(self, healthcare_data: HealthCareData):
        return self.__repo.create_object(**healthcare_data.dict())
