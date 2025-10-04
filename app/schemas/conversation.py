from typing import List

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str
    participants: List[int]


class ConversationUpdate(ConversationCreate): ...


class ConversationResponse(BaseModel):
    id: str
    title: str
    participants: List[str]
