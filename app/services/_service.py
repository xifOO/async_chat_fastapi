from typing import Generic, Sequence

from sqlalchemy.exc import IntegrityError

from app.db.db import db
from app.exceptions import RecordAlreadyExists
from app.repositories._repository import (
    AbstractRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        repository: AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType],
    ) -> None:
        self.repository = repository

    async def create(self, data: CreateSchemaType) -> ModelType:
        try:
            async with db.get_db_session() as session:
                return await self.repository.create(session, data=data)
        except IntegrityError:
            raise RecordAlreadyExists(status_code=400, detail="Record already exists")

    async def update(self, pk: int, data: UpdateSchemaType) -> ModelType:
        async with db.get_db_session() as session:
            return await self.repository.update(session, data=data, id=pk)

    async def delete(self, pk: int) -> None:
        async with db.get_db_session() as session:
            return await self.repository.delete(session, id=pk)

    async def find_one(self, **filters) -> ModelType | None:
        async with db.get_db_session() as session:
            return await self.repository.find_one(session, **filters)

    async def find_all(
        self, order: str = "id", limit: int = 100, offset: int = 0
    ) -> Sequence[ModelType]:
        async with db.get_db_session() as session:
            return await self.repository.find_all(
                session, order=order, limit=limit, offset=offset
            )
