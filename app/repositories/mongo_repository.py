from typing import Any, Dict, Optional, Type

from bson import ObjectId
from motor.core import AgnosticClientSession
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.repositories._repository import (
    AbstractRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)


class MongoDBRepository(
    AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType], collection_name: str):
        self.model = model
        self.collection_name = collection_name

    def get_collection(self, db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
        return db[self.collection_name]

    async def create(
        self,
        data: CreateSchemaType,
        db: AsyncIOMotorDatabase,
        session: AgnosticClientSession,
    ):
        collection = self.get_collection(db)

        doc = data.model_dump(exclude_unset=True)

        result = await collection.insert_one(doc, session=session)

        created_doc = await collection.find_one(
            {"_id": result.inserted_id}, session=session
        )
        return created_doc

    async def find_one(
        self, db: AsyncIOMotorDatabase, session: AgnosticClientSession, **filters
    ):
        collection = self.get_collection(db)
        return await collection.find_one(filters, session=session)

    async def find_all(
        self,
        db: AsyncIOMotorDatabase,
        session: AgnosticClientSession,
        skip: int = 0,
        limit: int = 100,
        **filters,
    ):
        collection = self.get_collection(db)

        cursor = collection.find(filters, session=session)

        cursor = cursor.skip(skip).limit(limit)

        return await cursor.to_list(length=limit)

    async def update(
        self,
        data: UpdateSchemaType,
        db: AsyncIOMotorDatabase,
        id: str | ObjectId,
        session: AgnosticClientSession,
    ):
        collection = self.get_collection(db)

        if isinstance(id, str):
            id = ObjectId(id)

        update_data = data.model_dump(exclude_unset=True)

        result = await collection.find_one_and_update(
            {"_id": id}, {"$set": update_data}, return_document=True, session=session
        )
        return result

    async def delete(
        self,
        db: AsyncIOMotorDatabase,
        id: str | ObjectId,
        session: Optional[AgnosticClientSession] = None,
    ) -> None:
        collection = self.get_collection(db)

        if isinstance(id, str):
            id = ObjectId(id)

        await collection.delete_one({"_id": id}, session=session)

    async def exists(
        self,
        db: AsyncIOMotorDatabase,
        filters: Dict[str, Any],
        session: Optional[AgnosticClientSession] = None,
    ) -> bool:
        collection = self.get_collection(db)
        count = await collection.count_documents(filters, limit=1, session=session)
        return count > 0
