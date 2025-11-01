from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field

from app.enum import AttachmentType
from app.models.mongo.base import PyObjectId


class Attachment(BaseModel):
    type: AttachmentType
    fileId: str
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    size: int
    metadata: dict = Field(default_factory=dict)


class AttachmentUpload(BaseModel):
    attachments: List[Attachment]


class AttachmentDownload(BaseModel):
    attachment: Attachment


class MessageContent(BaseModel):
    type: str
    text: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)


class MessageCreate(BaseModel):
    authorId: int
    conversationId: str
    content: MessageContent
    source: str


class MessageUpdate(BaseModel):
    content: Optional[MessageContent] = None


class MessageResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    authorId: int
    conversationId: PyObjectId
    content: MessageContent


class CacheMessage(MessageResponse):
    source: Literal["cache"] = "cache"


class DBMessage(MessageResponse):
    source: Literal["db"] = "db"


MessageType = Union[CacheMessage, DBMessage]