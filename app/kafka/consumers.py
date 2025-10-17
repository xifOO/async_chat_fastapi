from typing import Iterable

from app.types.channel import ConsumerChannelT
from app.types.message import Message
from app.types.transport import ConsumerT


class Consumer(ConsumerT):
    def __init__(self, channel: ConsumerChannelT) -> None:
        self._channel = channel
        self._closed = False
        self._subscribed = False

    async def consume(self) -> Message:
        if self._closed:
            raise RuntimeError("Consumer is closed")

        if not self._subscribed:
            raise RuntimeError("Consumer not subscribed")

        return await self._channel.consume()

    async def subscribe(self, topics: Iterable[str]) -> None:
        await self._channel.subscribe(topics=list(topics))
        self._subscribed = True

    async def commit(self) -> None:
        await self._channel.commit_offsets({})

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self.commit()
