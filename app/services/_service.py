from typing import Any, AsyncContextManager, Callable, Generic, List, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.exceptions import RecordAlreadyExists
from app.repositories._repository import (
    AbstractRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)

ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class BaseService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]
):
    def __init__(
        self,
        repository: AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType],
        response_schema: Type[ResponseSchemaType],
        db_session_factory: Callable[[], AsyncContextManager[Any]],
    ) -> None:
        self.repository = repository
        self.response_schema = response_schema
        self.db_session_factory = db_session_factory

    async def create(self, data: CreateSchemaType) -> ResponseSchemaType:
        try:
            async with self.db_session_factory() as session:
                record = await self.repository.create(session, data)
                return self.response_schema.model_validate(record)
        except IntegrityError:
            raise RecordAlreadyExists(status_code=400, detail="Record already exists")

    async def update(self, pk: int, data: UpdateSchemaType) -> ResponseSchemaType:
        async with self.db_session_factory() as session:
            record = await self.repository.update(session, data, id=pk)
            return self.response_schema.model_validate(record)

    async def delete(self, pk: Union[int, str]) -> None:
        async with self.db_session_factory() as session:
            return await self.repository.delete(session, id=pk)

    async def exists(self, **filters) -> bool:
        async with self.db_session_factory() as session:
            return await self.repository.exists(session, **filters)

    async def find_one(self, **filters) -> ResponseSchemaType | None:
        async with self.db_session_factory() as session:
            record = await self.repository.find_one(session, **filters)
            return self.response_schema.model_validate(record)

    async def find_all(
        self, order: str = "id", limit: int = 100, offset: int = 0, **filters
    ) -> List[ResponseSchemaType]:
        async with self.db_session_factory() as session:
            records = await self.repository.find_all(
                session, order=order, limit=limit, offset=offset, **filters
            )
            return [self.response_schema.model_validate(record) for record in records]
