import asyncio
from typing import Any, Awaitable, Optional

from app.kafka.channel import ProducerChannel
from app.types.channel import ProducerChannelT
from app.types.codecs import CodecArg
from app.types.message import K, V, FutureMessage, PendingMessage, RecordMetadata
from app.types.transport import Headers, ProducerBufferT, ProducerT

__all__ = ["Producer"]


class ProducerBuffer(ProducerBufferT):
    max_messages = 100

    def __init__(self, channel: ProducerChannelT) -> None:
        self.channel = channel
        self.pending: asyncio.Queue[FutureMessage] = asyncio.Queue(
            maxsize=self.max_messages
        )

    def put(self, fut: FutureMessage) -> None:
        if self.pending.full():
            fut.set_exception(asyncio.QueueFull("Producer buffer is full"))
            return
        self.pending.put_nowait(fut)

    async def flush(self) -> None:
        tasks = []

        while True:
            try:
                fut = self.pending.get_nowait()
            except asyncio.QueueEmpty:
                break
            else:
                tasks.append(self._send_pending(fut))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_pending(self, fut: FutureMessage) -> None:
        try:
            await self.channel.publish_message(fut, wait=False)
        except Exception as e:
            if not fut.done():
                fut.set_exception(e)

    @property
    def size(self) -> int:
        return self.pending.qsize()


class Producer(ProducerT):
    def __init__(self, **kwargs) -> None:
        self._channel = ProducerChannel(**kwargs)
        self._buffer = ProducerBuffer(self._channel)
        self._closed = True
    
    async def start(self) -> None:
        if not self._closed:
            return
        
        await self._channel.start()
        self._closed = False

    async def send(
        self,
        topic: str,
        key: K = None,
        value: V = None,
        headers: Optional[Headers] = None,
        *,
        timestamp: Optional[float] = None,
        key_serializer: Optional[CodecArg] = None,
        value_serializer: Optional[CodecArg] = None,
        **kwargs: Any,
    ) -> Awaitable[RecordMetadata]:
        if self._closed:
            raise RuntimeError("Producer is closed")

        pending = PendingMessage(
            key=key,
            value=value,
            timestamp=timestamp,
            headers=headers,
            key_serializer=key_serializer,
            value_serializer=value_serializer,
            topic=topic,
        )

        fut = FutureMessage(message=pending)
        self._buffer.put(fut)
        return fut

    async def flush(self) -> None:
        if self._closed:
            return 
        
        await self._buffer.flush()

    async def close(self) -> None:
        if self._closed:
            return 
        
        self._closed = True
        await self.flush()
        await self._channel.stop()
