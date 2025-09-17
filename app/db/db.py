from typing import Callable

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

database_url = URL.create(
    "postgresql+asyncpg",
    username=settings.postgres.username,
    password=settings.postgres.password,
    host=settings.postgres.host,
    port=settings.postgres.port,
    database=settings.postgres.database,
)

engine = create_async_engine(
    database_url,
    pool_size=settings.db_pool_conf.pool_size,
    max_overflow=settings.db_pool_conf.max_overflow,
    pool_timeout=settings.db_pool_conf.pool_timeout,
    pool_recycle=settings.db_pool_conf.pool_recycle,
    pool_pre_ping=settings.db_pool_conf.pool_pre_ping,
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def get_session_factory() -> Callable[[], AsyncSession]:
    return async_session_maker
