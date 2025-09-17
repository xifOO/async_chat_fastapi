from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel

from app.models.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    @abstractmethod
    async def create(self, data: CreateSchemaType) -> ModelType: ...

    @abstractmethod
    async def update(self, data: UpdateSchemaType, **kwargs) -> ModelType: ...

    @abstractmethod
    async def delete(self, **filters) -> None: ...

    @abstractmethod
    async def find_one(self, **kwargs) -> Optional[ModelType]: ...

    @abstractmethod
    async def find_all(
        self, order: str = "id", limit: int = 100, offset: int = 0
    ) -> Sequence[ModelType]: ...
