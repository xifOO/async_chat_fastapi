from typing import List, Optional

import redis.asyncio as redis
from bson import ObjectId
from redis.asyncio.client import Redis as AsyncRedis

from app.config import settings
from app.kafka.serializers import JSONCodec
from app.schemas.message import MessageUpdate


class RedisManager:
    def __init__(self) -> None:
        self._redis: Optional[AsyncRedis] = None
        self._pool = redis.ConnectionPool(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            max_connections=settings.redis.max_connections,
            decode_responses=True,
        )

    async def connect(self) -> None:
        if not self._redis:
            self._redis = redis.Redis(connection_pool=self._pool)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
        self._redis = None

    async def add_message(self, chat_key: str, message: dict) -> None:
        if not self._redis:
            return

        message_id = str(ObjectId())
        message["_id"] = message_id

        message_json = JSONCodec().dumps(message)
        key_list = f"chat:{chat_key}:messages"
        key_msg = f"chat:{chat_key}:messages:{message_id}"
        await self._redis.rpush(key_list, message_id)  # type: ignore
        await self._redis.set(key_msg, message_json)

    async def get_messages(self, conv_id: str, batch_size: int = 100) -> List[dict]:
        if not self._redis:
            return []

        key_list = f"chat:{conv_id}:messages"

        message_ids = await self._redis.lrange(key_list, -batch_size, -1)  # type: ignore

        if not message_ids:
            return []

        pipeline = self._redis.pipeline()
        for message_id in message_ids:
            key_msg = f"chat:{conv_id}:messages:{message_id}"
            pipeline.get(key_msg)

        messages = await pipeline.execute()

        return [JSONCodec().loads(m) for m in messages]

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

        message_ids = await self._redis.lrange(chat_key, 0, batch_size - 1)  # type: ignore

        if not message_ids:
            return []

        await self._redis.ltrim(chat_key, batch_size, -1)  # type: ignore

        pipeline = self._redis.pipeline()

        for message_id in message_ids:
            key_msg = f"{chat_key}:{message_id}"
            pipeline.get(key_msg)

        messages = await pipeline.execute()

        for message_id in message_ids:
            key_msg = f"{chat_key}:{message_id}"
            pipeline.delete(key_msg)
        await pipeline.execute()

        key_len = await self._redis.llen(chat_key)  # type: ignore
        if key_len == 0:
            await self._redis.delete(chat_key)

        return [JSONCodec().loads(m) for m in messages]

    async def delete_message(self, conv_id: str, message_id: str) -> None:
        if not self._redis:
            return

        key_list = f"chat:{conv_id}:messages"
        key_msg = f"chat:{conv_id}:messages:{message_id}"

        await self._redis.lrem(key_list, 1, message_id)  # type: ignore
        await self._redis.delete(key_msg)

    async def get_message(self, conv_id: str, message_id: str) -> Optional[dict]:
        if not self._redis:
            return

        key_msg = f"chat:{conv_id}:messages:{message_id}"

        raw = await self._redis.get(key_msg)

        if not raw:
            return None

        message = JSONCodec().loads(raw)
        return message

    async def update_message(
        self, conv_id: str, message_id: str, data: MessageUpdate
    ) -> Optional[dict]:
        if not self._redis:
            return

        message = await self.get_message(conv_id, message_id)

        if not message:
            return

        key_msg = f"chat:{conv_id}:messages:{message_id}"

        data_dict = data.model_dump()
        message["content"] = data_dict["content"]

        await self._redis.set(key_msg, JSONCodec().dumps(message))
        return message
