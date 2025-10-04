from typing import Annotated

from fastapi import APIRouter, Depends

from app.services.message import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


def get_message_service() -> MessageService:
    return MessageService()


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
