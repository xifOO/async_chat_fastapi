from app.services._service import BaseService


async def get_conversation(kwargs):
    service: BaseService = kwargs.get("service")
    conversation_id: str = kwargs.get("conversation_id")
    return await service.find_one(id=conversation_id)
