from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager

from motor.core import AgnosticClientSession
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.config import settings


class MongoSession:
    __slots__ = ("db", "session")

    def __init__(self, db: AsyncIOMotorDatabase, session: AgnosticClientSession):
        self.db = db
        self.session = session


class Database:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(
            f"mongodb://{settings.mongo.host}:{settings.mongo.port}?replicaSet=rs0"
        )
        self._db = self.client[settings.mongo.database]

    def __call__(self) -> AsyncContextManager[Any]:
        return self.get_db_session()

    @asynccontextmanager
    async def get_db_session(self):
        session = await self.client.start_session()
        try:
            async with session.start_transaction():
                yield MongoSession(db=self._db, session=session)
        except PyMongoError:
            raise
        finally:
            await session.end_session()


mongo_db = Database()
