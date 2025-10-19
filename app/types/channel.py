from abc import ABC, abstractmethod
from typing import Iterable, List, Mapping, Optional

from app.types.lifecycle import LifecycleT
from app.types.message import TP, FutureMessage, Message


class _ChannelT(LifecycleT, ABC): ...


class ProducerChannelT(_ChannelT):
    @abstractmethod
    async def publish_message(
        self, fut: FutureMessage, wait: bool = True, *, timeout: Optional[float] = 10.0
    ) -> None: ...


class ConsumerChannelT(_ChannelT):
    @abstractmethod
    async def consume(self, timeout: Optional[float] = 10.0) -> Message: ...

    @abstractmethod
    async def consume_batch(self, max_records: int, timeout: int) -> List[Message]: ...

    @abstractmethod
    def subscribe(self, topics: Iterable[str]) -> None: ...

    @abstractmethod
    async def commit_offsets(self, offsets: Mapping[TP, int]) -> None: ...
