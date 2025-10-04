from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel
from pymongo.errors import PyMongoError

from app.config import settings


class Database:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(
            f"mongodb://{settings.mongo.host}:{settings.mongo.port}"
        )
        self._db = self.client[settings.mongo.database]

    @asynccontextmanager
    async def get_db_session(self):
        session = await self.client.start_session()
        try:
            async with session.start_transaction():
                yield session
        except PyMongoError:
            raise
        finally:
            await session.end_session()

    async def write_indexes(self):
        await self._db.messages.create_indexes(
            [
                IndexModel([("conversationId", ASCENDING), ("createdAt", DESCENDING)]),
                IndexModel([("conversationId", ASCENDING), ("_id", DESCENDING)]),
                IndexModel([("messageId", ASCENDING)], unique=True),
                IndexModel([("authorId", ASCENDING), ("createdAt", DESCENDING)]),
                IndexModel([("content.text", TEXT)]),
            ]
        )

        await self._db.conversations.create_indexes(
            [
                IndexModel([("conversationId", ASCENDING)], unique=True),
                IndexModel(
                    [("participants.userId", ASCENDING), ("updatedAt", DESCENDING)]
                ),
                IndexModel([("updatedAt", DESCENDING)]),
            ]
        )


mongo_db = Database()
