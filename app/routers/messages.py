from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.permissions.decorators import check_own_or_permission, requires_check
from app.permissions.getters import get_message
from app.services.message import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


def get_message_service() -> MessageService:
    return MessageService()


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]


@router.delete("/{message_id}", status_code=204)
@requires_check(check_own_or_permission("message", "delete", get_object=get_message))
async def delete_message(request: Request, service: MessageServiceDep, message_id: str):
    await service.delete(pk=message_id)
    return Response(status_code=204)
