from contextlib import asynccontextmanager

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


class Database:
    def __init__(self) -> None:
        database_url = URL.create(
            "postgresql+asyncpg",
            username=settings.postgres.username,
            password=settings.postgres.password,
            host=settings.postgres.host,
            port=settings.postgres.port,
            database=settings.postgres.database,
        )

        self.engine = create_async_engine(
            database_url,
            pool_size=settings.db_pool_conf.pool_size,
            max_overflow=settings.db_pool_conf.max_overflow,
            pool_timeout=settings.db_pool_conf.pool_timeout,
            pool_recycle=settings.db_pool_conf.pool_recycle,
            pool_pre_ping=settings.db_pool_conf.pool_pre_ping,
        )

        self._session_factory = async_sessionmaker(
            self.engine, autocommit=False, autoflush=False, expire_on_commit=False
        )

    @asynccontextmanager
    async def get_db_session(self):
        from sqlalchemy import exc

        session: AsyncSession = self._session_factory()
        try:
            async with session.begin():
                yield session
        except exc.SQLAlchemyError:
            raise
        finally:
            await session.close()


db = Database()
