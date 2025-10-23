from typing import Iterable, List

from app.kafka.channel import ConsumerChannel
from app.types.message import Message
from app.types.transport import ConsumerT


class Consumer(ConsumerT):
    def __init__(self, **kwargs) -> None:
        self._channel = ConsumerChannel(**kwargs)
        self._closed = True
        self._subscribed = False

    async def start(self) -> None:
        if not self._closed:
            return

        await self._channel.start()
        self._closed = False

    async def consume(self) -> Message:
        if self._closed:
            raise RuntimeError("Consumer is closed")

        if not self._subscribed:
            raise RuntimeError("Consumer not subscribed")

        return await self._channel.consume()

    async def consume_batch(self, max_records: int, timeout: int) -> List[Message]:
        if self._closed:
            raise RuntimeError("Consumer is closed")

        if not self._subscribed:
            raise RuntimeError("Consumer not subscribed")

        return await self._channel.consume_batch(max_records, timeout)

    def subscribe(self, topics: Iterable[str]) -> None:
        self._channel.subscribe(topics=list(topics))
        self._subscribed = True

    async def commit(self) -> None:
        await self._channel.commit_offsets({})

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        await self.commit()
        await self._channel.stop()
