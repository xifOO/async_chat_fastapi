import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import URL, NullPool
from app.models.base_model import Base
from app.models.models import *
from app.db.db import Database


class TestDatabase(Database):
    def __init__(self) -> None:
        database_url = URL.create(
            "postgresql+asyncpg",
            username=os.getenv("POSTGRES_USERNAME"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"), # type: ignore[arg-type]
            database=os.getenv("POSTGRES_DATABASE"),
        )

        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            poolclass=NullPool
        )

        self._session_factory = async_sessionmaker(
            self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )


@pytest_asyncio.fixture(scope="session")
async def test_db():
    db = TestDatabase()
    yield db
    await db.engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(test_db):
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def test_session(test_db):
    async with test_db.get_db_session() as session:
        yield session
