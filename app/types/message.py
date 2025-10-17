import asyncio
from typing import (
    Awaitable,
    NamedTuple,
    Optional,
    Union,
)

from pydantic import BaseModel

from app.models.base_model import Base
from app.types.codecs import CodecArg
from app.types.transport import Headers, OpenHeaders

SerializableKey = Union[bytes, str, int, float]
SerializableValue = Union[bytes, str, dict, list, int, float]

ModelLike = Union[BaseModel, Base]

K = Optional[Union[SerializableKey, ModelLike]]
V = Optional[Union[SerializableValue, ModelLike]]


class TP(NamedTuple):
    topic: str
    partition: int


class RecordMetadata(NamedTuple):
    topic: str
    partition: int
    topic_partition: TP
    offset: int
    timestamp: Optional[float] = None


class PendingMessage(NamedTuple):
    key: K
    value: V
    partition: Optional[int]
    timestamp: Optional[float]
    headers: Optional[Headers]
    key_serializer: CodecArg
    value_serializer: CodecArg
    topic: Optional[str] = None


class FutureMessage(asyncio.Future, Awaitable[RecordMetadata]):
    message: PendingMessage

    def __init__(self, message: PendingMessage) -> None:
        self.message = message
        super().__init__()

    def set_result(self, result: RecordMetadata) -> None:
        return super().set_result(result)


class Message(NamedTuple):
    topic: str
    partition: int
    offset: int
    key: Optional[bytes]
    value: Optional[bytes]
    headers: Optional[OpenHeaders]
    timestamp: Optional[float]

    @property
    def tp(self) -> TP:
        return TP(self.topic, self.partition)
