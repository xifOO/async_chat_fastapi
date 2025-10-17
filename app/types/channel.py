from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Optional

from app.types.message import TP, FutureMessage, Message


class _ChannelT(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...


class ProducerChannelT(_ChannelT):
    @abstractmethod
    async def publish_message(
        self, fut: FutureMessage, wait: bool = True, *, timeout: Optional[float] = 10.0
    ) -> None: ...


class ConsumerChannelT(_ChannelT):
    @abstractmethod
    async def consume(self, timeout: Optional[float] = 10.0) -> Message: ...

    @abstractmethod
    def subscribe(self, topics: Iterable[str]) -> None: ...

    @abstractmethod
    async def commit_offsets(self, offsets: Mapping[TP, int]) -> None: ...
