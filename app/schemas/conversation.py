from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.mongo.base import PyObjectId


class ConversationCreate(BaseModel):
    title: str
    participants: List[int]


class ConversationUpdate(ConversationCreate): ...


class ConversationResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    participants: List[int]

    model_config = ConfigDict(alias_generator=None)
