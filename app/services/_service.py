from typing import Generic, Sequence

from app.repositories._repository import (
    AbstractRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)
from app.uow.uow import AbstractUnitOfWork


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        repository: AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType],
        uow: AbstractUnitOfWork,
    ) -> None:
        self.repository = repository
        self.uow = uow

    async def create(self, data: CreateSchemaType) -> ModelType:
        return await self.repository.create(data=data)

    async def update(self, pk: int, data: UpdateSchemaType) -> ModelType:
        return await self.repository.update(data=data, id=pk)

    async def delete(self, pk: int) -> None:
        return await self.repository.delete(id=pk)

    async def find_one(self, **filters) -> ModelType | None:
        return await self.repository.find_one(**filters)

    async def find_all(
        self, order: str = "id", limit: int = 100, offset: int = 0
    ) -> Sequence[ModelType]:
        return await self.repository.find_all(order=order, limit=limit, offset=offset)
