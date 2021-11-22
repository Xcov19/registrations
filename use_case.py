import functools
from typing import Callable
from typing import Type

from entities import HealthCareEntity as HealthCareEntity
from entities import HealthCareRecordEntity
from interfaces import RepoInterface


@functools.lru_cache
def register_use_case(use_case_callable: Callable, repo_callable: Callable):
    return use_case_callable(repo_callable)


class HospitalRegistrationUseCase:
    def __init__(
        self, repo: Type[RepoInterface]
    ):  # i.e. Union[Type[PsqlRepo], Type[MongoRepo]]
        self.__repo = repo

    async def valid_new_entry(self, healthcare_data: HealthCareEntity) -> bool:
        """
        TODO: Builds tools where we can fire off async processes to check for:
            1. valid hospital phone.
            2. clerical verification by phone.
            3. correct hospital incorporation info.
        :param healthcare_data: HealthCareEntity, health care data.
        :return: bool, whether data is valid.
        """

        return await self.__repo.validate_entry(**healthcare_data.dict())

    async def duplicate_exists(self, healthcare_data: HealthCareEntity) -> bool:
        return await self.__repo.is_duplicate(**healthcare_data.dict())

    async def create_entry(
        self, healthcare_data: HealthCareEntity
    ) -> HealthCareRecordEntity:
        return await self.__repo.create_object(**healthcare_data.dict())
