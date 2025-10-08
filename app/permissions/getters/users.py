from fastapi import Request

from app.services._service import BaseService


async def get_user(request: Request, kwargs):
    service: BaseService = kwargs.get("service")
    user_id: str = kwargs.get("user_id")
    return await service.find_one(id=user_id)
