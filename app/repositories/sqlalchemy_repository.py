from typing import Sequence, Type

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories._repository import (
    AbstractRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)


class SqlAlchemyRepository(
    AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession) -> None:
        self.session = db_session
        self.model = model

    async def create(self, data: CreateSchemaType) -> ModelType:
        instance = self.model(**data.model_dump())
        self.session.add(instance)
        return instance

    async def update(self, data: UpdateSchemaType, **filters) -> ModelType:
        update_data = data.model_dump(exclude_unset=True)
        stmt = (
            update(self.model)
            .values(**update_data)
            .filter_by(**filters)
            .returning(self.model)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete(self, **filters) -> None:
        await self.session.execute(delete(self.model).filter_by(**filters))

    async def find_one(self, **filters) -> ModelType | None:
        row = await self.session.execute(select(self.model).filter_by(**filters))
        return row.scalar_one_or_none()

    async def find_all(
        self, order: str = "id", limit: int = 100, offset: int = 0
    ) -> Sequence[ModelType]:
        stmt = select(self.model).order_by(order).limit(limit).offset(offset)
        row = await self.session.execute(stmt)
        return row.scalars().all()
