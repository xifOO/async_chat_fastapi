from typing import List

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.models.mixins import TimeStampMixin
from app.models.mongo.base import PyObjectId
from app.schemas.message import MessageContent


class MessageModel(BaseModel, TimeStampMixin):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    authorId: int
    conversationId: str
    content: MessageContent

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
    )


class ConversationModel(BaseModel, TimeStampMixin):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    participants: List[int] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
    )
