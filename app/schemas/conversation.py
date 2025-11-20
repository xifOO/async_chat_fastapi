from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.mongo.base import PyObjectId
from app.schemas.user import UserResponse


class ConversationCreate(BaseModel):
    title: str
    participants: List[int]


class ConversationUpdate(ConversationCreate): ...


class ConversationResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    participants: List[int]

    model_config = ConfigDict(alias_generator=None)


class ConversationWithUsersResponse(BaseModel):
    conversation: ConversationResponse
    users: List[UserResponse] = Field(default_factory=list)
