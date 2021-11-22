import functools
from typing import Callable
from typing import Type

from entities import HealthCareEntity as HealthCareEntity
from entities import HealthCareRecordEntity
from entities import HospitalOnlyEntity
from errors import DuplicateEntryException
from errors import InvalidEntryException
from interfaces import RepoInterface


@functools.lru_cache
def register_use_case(use_case_callable: Callable, repo_callable: Callable):
    return use_case_callable(repo_callable)


class HospitalRegistrationUseCase:
    """Service logic adapter for hospital registration."""

    exclude_fields = {
        "location",
        "registering_user_info",
    }

    def __init__(
        self, repo: Type[RepoInterface]
    ):  # i.e. Union[Type[PsqlRepo], Type[MongoRepo]]
        self.__repo = repo

    async def valid_new_entry(self, healthcare_data: HospitalOnlyEntity) -> bool:
        """
        TODO: Builds tools where we can fire off async processes to check for:
            1. valid hospital phone.
            2. clerical verification by phone.
            3. correct hospital incorporation info.
        :param healthcare_data: HealthCareEntity, health care data.
        :return: bool, whether data is valid.
        """

        return await self.__repo.validate_entry(**healthcare_data.dict())

    async def duplicate_exists(self, healthcare_data: HospitalOnlyEntity) -> bool:
        return await self.__repo.is_duplicate(**healthcare_data.dict())

    async def create_entry(
        self, healthcare_data: HealthCareEntity
    ) -> HealthCareRecordEntity:
        return await self.__repo.create_object(**healthcare_data.dict())

    async def save(self, healthcare_data: HealthCareEntity) -> HealthCareRecordEntity:
        """Validates and saves healthcare input."""
        test_healthcare_data = HospitalOnlyEntity(**healthcare_data.dict())
        if not await self.valid_new_entry(test_healthcare_data):
            raise InvalidEntryException(detail="Not a valid entry.")
        if await self.duplicate_exists(test_healthcare_data):
            raise DuplicateEntryException(detail=f"Entry already exists.")
        return await self.create_entry(healthcare_data)
