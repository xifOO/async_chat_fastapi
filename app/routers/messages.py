from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.permissions.decorators import check_own_or_permission, requires_check
from app.permissions.getters import get_message
from app.schemas.message import MessageUpdate
from app.services.message import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


def get_message_service() -> MessageService:
    return MessageService()


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]


@router.delete("/{message_id}", status_code=204)
@requires_check(
    check_own_or_permission(
        "message", "delete", get_object=get_message, owner_field="authorId"
    )
)
async def delete_message(request: Request, service: MessageServiceDep, message_id: str):
    await service.delete(pk=message_id)
    return Response(status_code=204)


@router.patch("/{message_id}")
@requires_check(
    check_own_or_permission(
        "message", "update", get_object=get_message, owner_field="authorId"
    )
)
async def update_message(
    request: Request, service: MessageServiceDep, message_id: str, data: MessageUpdate
):
    message = await service.update(pk=message_id, data=data)
    return message
