from typing import Annotated, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.aws import AWSManager
from app.dependencies import RedisManagerDep
from app.enum import IncludeParams
from app.exceptions import AWSDownloadError, AWSUploadError
from app.permissions.decorators import requires_check
from app.routers.messages import MessageServiceDep
from app.routers.users import UserServiceDep
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithUsersResponse,
)
from app.schemas.message import (
    AttachmentDownload,
    AttachmentUpload,
    CacheMessage,
    DBMessage,
)
from app.services.conversation import ConversationService
from app.utils import load_messages

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_conv_service() -> ConversationService:
    return ConversationService()


async def get_aws_manager() -> AWSManager:
    return AWSManager()


AWSManagerDep = Annotated[AWSManager, Depends(get_aws_manager)]
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
    include: Optional[str] = Query(
        None, description="Include related resources (see IncludeParams enum)"
    ),
):
    conversation = await service.find_one(id=conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    users = []
    if include == IncludeParams.PARTICIPANTS:
        users = await user_service.find_in(conversation.participants)

    return ConversationWithUsersResponse(conversation=conversation, users=users)


@router.post("/", response_model=ConversationResponse)
@requires_check()
async def create_conversation(
    request: Request, data: ConversationCreate, service: ConvServiceDep
):
    if request.user.id not in data.participants:
        data.participants.append(request.user.id)

    new_conv = await service.create(data)
    return new_conv


@router.get("/{conv_id}/messages", response_model=List[Union[CacheMessage, DBMessage]])
async def get_conversation_messages(
    conv_id: str,
    service: MessageServiceDep,
    redis: RedisManagerDep,
):
    messages = await load_messages(service, redis, conv_id)
    return messages


@router.post("/{conv_id}/upload-urls")
async def get_upload_urls(
    conv_id: str, attachments: AttachmentUpload, aws: AWSManagerDep
):
    if not attachments:
        raise HTTPException(status_code=400, detail="No attachments provided")

    upload_urls = []

    for attachment in attachments.attachments:
        try:
            url = await aws.upload_file(
                file_name=attachment.metadata["originalName"],
                file_type=attachment.metadata["mimeType"],
                file_etag=attachment.metadata["etag"],
            )
        except AWSUploadError:
            raise HTTPException(status_code=500, detail="Failed to upload file.")

        upload_urls.append({"fileId": attachment.fileId, "url": url})

    return {"urls": upload_urls}


@router.post("/{conv_id}/download-urls")
async def get_download_urls(
    conv_id: str, attachment: AttachmentDownload, aws: AWSManagerDep
):
    if not attachment:
        raise HTTPException(status_code=400, detail="No attachments provided")

    try:
        url = await aws.download_file(
            file_name=attachment.attachment.metadata["originalName"],
            file_type=attachment.attachment.metadata["mimeType"],
        )
    except AWSDownloadError:
        raise HTTPException(status_code=500, detail="Failed to download file.")

    return {"url": url}
