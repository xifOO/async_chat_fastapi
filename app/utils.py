from typing import List

from app.cache import RedisManager
from app.schemas.message import MessageResponse
from app.services.message import MessageService


async def load_messages(service: MessageService, conv_id: str) -> List[dict]:
    redis = RedisManager()
    await redis.connect()

    messages = []

    r_records = await redis.get_messages(
        f"chat:{conv_id}:messages", batch_size=100
    )  # later from settings.batch_size
    if r_records:
        r_messages = [MessageResponse.model_validate(record) for record in r_records]
        messages.extend(r_messages)

    remaining = 100 - len(messages)  # later from settings.batch_size
    if remaining > 0:
        db_messages = await service.find_all(conversationId=conv_id, limit=remaining)
        messages.extend(db_messages)

    messages = sorted(messages, key=lambda m: m.id)
    return messages
