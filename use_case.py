from typing import Type

from models import HealthCareData
from repo import MongoRepo


class HospitalRegistrationUseCase:
    def __init__(self, repo: Type[MongoRepo]):
        self.__repo = repo

    async def valid_new_entry(self, healthcare_data: HealthCareData) -> bool:
        return await self.__repo.validate_entry(**healthcare_data.dict())

    async def duplicate_exists(self, healthcare_data: HealthCareData) -> bool:
        return await self.__repo.is_duplicate(**healthcare_data.dict())

    async def create_entry(self, healthcare_data: HealthCareData) -> HealthCareData:
        return await self.__repo.create_object(**healthcare_data.dict())
