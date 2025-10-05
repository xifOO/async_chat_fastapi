from typing import List, Optional

from pydantic import BaseModel, Field

from app.enum import AttachmentType
from app.models.mongo.base import PyObjectId


class Attachment(BaseModel):
    type: AttachmentType
    fileId: str
    url: str
    thumbnail: Optional[str] = None
    size: int
    metadata: dict = Field(default_factory=dict)


class MessageContent(BaseModel):
    type: str
    text: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)


class MessageCreate(BaseModel):
    authorId: int
    conversationId: str  
    content: MessageContent


class MessageUpdate(MessageCreate): ...


class MessageResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    authorId: int
    conversationId: PyObjectId
    content: MessageContent
