from typing import Type

from entities import HealthCareData, NewHealthCareData
from repo import MongoRepo


class HospitalRegistrationUseCase:
    def __init__(self, repo: Type[MongoRepo]):
        self.__repo = repo

    def valid_new_entry(self, healthcare_data: HealthCareData) -> bool:
        return self.__repo.validate_entry(**healthcare_data.dict())

    def duplicate_exists(self, healthcare_data: HealthCareData) -> bool:
        return self.__repo.is_duplicate(**healthcare_data.dict())

    async def create_entry(self, healthcare_data: HealthCareData) -> NewHealthCareData:
        return self.__repo.create_object(**healthcare_data.dict())
