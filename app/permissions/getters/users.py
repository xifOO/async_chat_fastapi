from app.services._service import BaseService


async def get_user(kwargs):
    service: BaseService = kwargs.get("service")
    user_id: str = kwargs.get("user_id")
    return await service.find_one(id=user_id)
