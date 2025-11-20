from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, Response

from app.dependencies import RedisManagerDep
from app.permissions.decorators import check_own_or_permission, requires_check
from app.permissions.getters import get_cache_message, get_db_message
from app.schemas.message import MessageUpdate
from app.services.message import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


def get_message_service() -> MessageService:
    return MessageService()


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]


@router.delete("/{message_id}", status_code=204)
@requires_check(
    check_own_or_permission(
        "message", "delete", get_object=get_db_message, owner_field="authorId"
    )
)
async def delete_db_message(service: MessageServiceDep, message_id: str):
    await service.delete(pk=message_id)
    return Response(status_code=204)


@router.delete("/{message_id}/cache", status_code=204)
@requires_check(
    check_own_or_permission(
        "message", "delete", get_object=get_cache_message, owner_field="authorId"
    )
)
async def delete_cache_message(
    service: RedisManagerDep,
    message_id: str,
    conv_id: Annotated[str, Query(...)],
):
    await service.delete_message(conv_id, message_id)
    return Response(status_code=204)


@router.patch("/{message_id}")
@requires_check(
    check_own_or_permission(
        "message", "update", get_object=get_db_message, owner_field="authorId"
    )
)
async def update_db_message(
    service: MessageServiceDep, message_id: str, data: MessageUpdate
):
    message = await service.update(pk=message_id, data=data)
    return message


@router.patch("/{message_id}/cache")
@requires_check(
    check_own_or_permission(
        "message", "update", get_object=get_cache_message, owner_field="authorId"
    )
)
async def update_cache_message(
    service: RedisManagerDep,
    message_id: str,
    data: Annotated[MessageUpdate, Body(...)],
    conv_id: Annotated[str, Query(...)],
):
    message = await service.update_message(
        conv_id=conv_id, message_id=message_id, data=data
    )
    return message
