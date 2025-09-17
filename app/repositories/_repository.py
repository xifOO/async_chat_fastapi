from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    @abstractmethod
    async def create(
        self, session: AsyncSession, data: CreateSchemaType
    ) -> ModelType: ...

    @abstractmethod
    async def update(
        self, session: AsyncSession, data: UpdateSchemaType, **kwargs
    ) -> ModelType: ...

    @abstractmethod
    async def delete(self, session: AsyncSession, **filters) -> None: ...

    @abstractmethod
    async def find_one(
        self, session: AsyncSession, **kwargs
    ) -> Optional[ModelType]: ...

    @abstractmethod
    async def find_all(
        self,
        session: AsyncSession,
        order: str = "id",
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ModelType]: ...
