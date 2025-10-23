from typing import List, Optional

import redis.asyncio as redis
from redis.asyncio.client import Redis as AsyncRedis

from app.config import settings
from app.kafka.serializers import JSONCodec


class RedisManager:
    def __init__(self) -> None:
        self._redis: Optional[AsyncRedis] = None
        self._pool: Optional[redis.ConnectionPool] = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = redis.ConnectionPool(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                max_connections=settings.redis.max_connections,
                decode_responses=True,
            )
            self._redis = redis.Redis(connection_pool=self._pool)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()
        self._redis = None
        self._pool = None

    async def add_message(self, chat_key: str, message: dict) -> None:
        if not self._redis:
            return
        message_json = JSONCodec().dumps(message)
        await self._redis.rpush(chat_key, message_json)  # type: ignore

    async def delete_key(self, chat_key: str) -> Optional[int]:
        if self._redis:
            return await self._redis.delete(chat_key)
        return None

    async def get_messages(self, chat_key: str, batch_size: int = 100) -> List[dict]:
        if not self._redis:
            return []

        codec = JSONCodec()
        messages_json = await self._redis.lrange(chat_key, -batch_size, -1)  # type: ignore
        return [codec.loads(m) for m in messages_json]

    async def get_batch(
        self, cursor: int = 0, count: int = 10
    ) -> tuple[int, List[str]]:
        if not self._redis:
            return 0, []

        cursor, keys = await self._redis.scan(
            cursor=cursor,
            match="chat:*:messages",  # later: change
            count=count,
        )
        return cursor, keys

    async def pop_messages(self, chat_key: str, batch_size: int = 100) -> List[dict]:
        if not self._redis:
            return []

        codec = JSONCodec()
        pipeline = self._redis.pipeline()

        pipeline.lrange(chat_key, 0, batch_size - 1)
        pipeline.ltrim(chat_key, batch_size, -1)

        result = await pipeline.execute()
        messages_json = result[0]

        if not messages_json:
            await self._redis.delete(chat_key)
            return []

        return [codec.loads(m) for m in messages_json]
