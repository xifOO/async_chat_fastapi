from typing import Sequence, Type

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import RecordAlreadyExists
from app.repositories._repository import (
    AbstractRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)


class SqlAlchemyRepository(
    AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def create(self, session: AsyncSession, data: CreateSchemaType) -> ModelType:
        try:
            instance = self.model(**data.model_dump())
            session.add(instance)
            return instance
        except IntegrityError:
            raise RecordAlreadyExists()

    async def update(
        self, session: AsyncSession, data: UpdateSchemaType, **filters
    ) -> ModelType:
        update_data = data.model_dump(exclude_unset=True)
        stmt = (
            update(self.model)
            .values(**update_data)
            .filter_by(**filters)
            .returning(self.model)
        )
        res = await session.execute(stmt)
        return res.scalar_one()

    async def delete(self, session: AsyncSession, **filters) -> None:
        await session.execute(delete(self.model).filter_by(**filters))

    async def find_one(self, session: AsyncSession, **filters) -> ModelType | None:
        row = await session.execute(select(self.model).filter_by(**filters))
        return row.scalar_one_or_none()

    async def find_all(
        self,
        session: AsyncSession,
        order: str = "id",
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ModelType]:
        stmt = select(self.model).order_by(order).limit(limit).offset(offset)
        row = await session.execute(stmt)
        return row.scalars().all()
