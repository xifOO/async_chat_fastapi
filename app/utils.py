from typing import List

from app.cache import RedisManager
from app.schemas.message import CacheMessage, DBMessage, MessageType
from app.services.message import MessageService


async def load_messages(service: MessageService, conv_id: str) -> List[MessageType]:
    redis = RedisManager()
    await redis.connect()

    messages: List[MessageType] = []

    cached = await redis.get_messages(
        f"chat:{conv_id}:messages", batch_size=100
    )  # later from settings.batch_size
    if cached:
        messages.extend(CacheMessage.model_validate(r) for r in cached)

    remaining = 100 - len(messages)  # later from settings.batch_size
    if remaining > 0:
        db_records = await service.find_all(conversationId=conv_id, limit=remaining)
        messages.extend(
            DBMessage.model_validate({**m.model_dump(), "_id": m.model_dump().pop("id")})
            for m in db_records
        )

    messages = sorted(messages, key=lambda m: m.id)
    return messages
