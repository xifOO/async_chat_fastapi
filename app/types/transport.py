import asyncio
from abc import ABC, abstractmethod
from typing import (
    Any,
    Awaitable,
    ClassVar,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from app.types.codecs import CodecArg
from app.types.message import FutureMessage, Message, RecordMetadata

Headers = Union[List[Tuple[str, bytes]], Mapping[str, bytes]]
OpenHeaders = Union[Sequence[Tuple[str, bytes]]]


class ServiceT(ABC):
    transport: "TransportT"

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def process(self) -> None: ...


class ConsumerT(ABC):
    @abstractmethod
    async def consume(self) -> Message: ...

    @abstractmethod
    async def subscribe(self, topics: Iterable[str]) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...


class ProducerBufferT(ABC):
    max_messages: ClassVar[int]

    pending: asyncio.Queue

    @abstractmethod
    def put(self, fut: FutureMessage) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...

    @property
    @abstractmethod
    def size(self) -> int: ...


class ProducerT(ABC):
    _buffer = ProducerBufferT

    @abstractmethod
    async def send(
        self,
        topic: str,
        key: Optional[bytes],
        value: Optional[bytes],
        partition: Optional[int],
        headers: Optional[Headers],
        *,
        timestamp: Optional[float] = None,
        key_serializer: Optional[CodecArg] = None,
        value_serializer: Optional[CodecArg] = None,
        **kwargs: Any,
    ) -> Awaitable[RecordMetadata]: ...

    @abstractmethod
    async def create_topic(
        self,
        topic: str,
        partitions: int,
        replication: int,
        *,
        delete: Optional[bool] = None,
    ) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...


class TransportT(ABC):
    Consumer: ClassVar[Type[ConsumerT]]
    Producer: ClassVar[Type[ProducerT]]

    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    def create_consumer(self, **kwargs: Any) -> ConsumerT: ...

    @abstractmethod
    def create_producer(self, **kwargs: Any) -> ProducerT: ...
