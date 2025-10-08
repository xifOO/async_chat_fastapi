from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.enum import IncludeParams
from app.permissions import requires_check
from app.routers.messages import MessageServiceDep
from app.routers.users import UserServiceDep
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithUsersResponse,
)
from app.schemas.message import MessageResponse
from app.services.conversation import ConversationService


router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_conv_service() -> ConversationService:
    return ConversationService()


ConvServiceDep = Annotated[ConversationService, Depends(get_conv_service)]


@router.get("/", response_model=List[ConversationResponse])
@requires_check()
async def get_user_conversations(request: Request, service: ConvServiceDep):
    conversations = await service.find_all(participants=request.user.id)
    return conversations


@router.get("/{conv_id}", response_model=ConversationWithUsersResponse)
async def get_conversation(
    conv_id: str,
    service: ConvServiceDep,
    user_service: UserServiceDep,
    include: Optional[str] = Query(None, description="Include related resources (see IncludeParams enum)"),
):
    conversation = await service.find_one(id=conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    users = []
    if include == IncludeParams.PARTICIPANTS:
        users = await user_service.find_in(conversation.participants)

    return ConversationWithUsersResponse(
        conversation=conversation,
        users=users
    )


@router.post("/", response_model=ConversationResponse)
@requires_check()
async def create_conversation(
    request: Request, data: ConversationCreate, service: ConvServiceDep
):
    if request.user.id not in data.participants:
        data.participants.append(request.user.id)

    new_conv = await service.create(data)
    return new_conv


@router.get("/{conv_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conv_id: str, service: MessageServiceDep):
    messages = await service.find_all(conversationId=conv_id)
    return messages
