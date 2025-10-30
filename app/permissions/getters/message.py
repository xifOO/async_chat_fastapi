from fastapi import Request

from app.cache import RedisManager
from app.services._service import BaseService


async def get_db_message(request: Request, kwargs):
    service: BaseService = kwargs.get("service")
    message_id: str = kwargs.get("message_id")
    return await service.find_one(id=message_id)


async def get_cache_message(request: Request, kwargs):
    service: RedisManager = kwargs.get("service")
    message_id: str = kwargs.get("message_id")
    conv_id: str = kwargs.get("conv_id")
    return await service.get_message(conv_id, message_id)

