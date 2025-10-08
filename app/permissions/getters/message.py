from fastapi import Request

from app.services._service import BaseService


async def get_message(request: Request, kwargs):
    service: BaseService = kwargs.get("service")
    message_id: str = kwargs.get("message_id")
    return await service.find_one(id=message_id)
