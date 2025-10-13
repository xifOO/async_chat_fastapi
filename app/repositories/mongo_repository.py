from typing import Type

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.db.mongo import MongoSession
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

    def _transform_objectid_fields(self, filters: dict) -> dict:
        filters = filters.copy()
        for field in ["id"]:
            if field in filters:
                _id = filters.pop(field)
                if ObjectId.is_valid(_id):
                    filters["_id" if field == "id" else field] = ObjectId(_id)
        return filters

    async def create(
        self,
        session: MongoSession,
        data: CreateSchemaType,
    ) -> ModelType:
        collection = self.get_collection(session.db)

        doc = data.model_dump(exclude_unset=True)

        result = await collection.insert_one(doc, session=session.session)

        created_doc = await collection.find_one(
            {"_id": result.inserted_id}, session=session.session
        )
        return created_doc

    async def find_one(self, session: MongoSession, **filters):
        collection = self.get_collection(session.db)

        filters = self._transform_objectid_fields(filters)

        return await collection.find_one(filters, session=session.session)

    async def find_all(
        self,
        session: MongoSession,
        order: str = "id",
        limit: int = 100,
        offset: int = 0,
        **filters,
    ):
        collection = self.get_collection(session.db)

        filters = self._transform_objectid_fields(filters)

        cursor = collection.find(filters, session=session.session)

        if order:
            sort_field = "_id" if order == "id" else order
            cursor = cursor.sort(sort_field, 1)

        cursor = cursor.skip(offset).limit(limit)

        return await cursor.to_list(length=limit)

    async def update(
        self,
        session: MongoSession,
        data: UpdateSchemaType,
        id: str | ObjectId,
    ):
        collection = self.get_collection(session.db)

        if isinstance(id, str):
            id = ObjectId(id)

        update_data = data.model_dump(exclude_unset=True)

        result = await collection.find_one_and_update(
            {"_id": id},
            {"$set": update_data},
            return_document=True,
            session=session.session,
        )
        return result

    async def delete(
        self,
        session: MongoSession,
        id: str | ObjectId,
    ) -> None:
        collection = self.get_collection(session.db)

        if isinstance(id, str):
            id = ObjectId(id)

        await collection.delete_one({"_id": id}, session=session.session)

    async def exists(
        self,
        session: MongoSession,
        **filters,
    ) -> bool:
        collection = self.get_collection(session.db)

        filters = self._transform_objectid_fields(filters)

        count = await collection.count_documents(
            filters, limit=1, session=session.session
        )
        return count > 0
