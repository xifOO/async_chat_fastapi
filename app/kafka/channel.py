import asyncio
from email import message
from typing import Iterable, List, Mapping, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, TopicPartition

from app.config import settings
from app.kafka.serializers import serialize
from app.types.channel import ConsumerChannelT, ProducerChannelT
from app.types.message import TP, FutureMessage, Message, RecordMetadata


class ProducerChannel(ProducerChannelT):
    def __init__(self) -> None:
        super().__init__()
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.bootstrap_servers
        )

    async def start(self) -> None:
        await self._producer.start()
        self._ready.set()

    async def stop(self) -> None:
        if self._closed:
            return

        self._closed = True
        self._ready.clear()
        await self._producer.stop()

    async def publish_message(
        self, fut: FutureMessage, wait: bool = True, *, timeout: Optional[float] = 10.0
    ) -> None:
        try:
            await asyncio.wait_for(self._ready.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            fut.set_exception(RuntimeError("Producer channel not ready"))
            return

        if self._closed:
            fut.set_exception(RuntimeError("Producer channel is closed"))
            return

        pending = fut.message

        try:
            key_bytes = serialize(pending.key, pending.key_serializer)
            value_bytes = serialize(pending.value, pending.value_serializer)

            res = await self._producer.send_and_wait(
                topic=pending.topic,
                key=key_bytes,
                value=value_bytes,
                partition=pending.partition,
                headers=pending.headers,
            )

            fut.set_result(
                RecordMetadata(
                    topic=res.topic,
                    partition=res.partition,
                    topic_partition=TP(res.topic, res.partition),
                    offset=res.offset,
                    timestamp=getattr(res, "timestamp", None),
                )
            )
        except Exception as exc:
            fut.set_exception(exc)


class ConsumerChannel(ConsumerChannelT):
    def __init__(self) -> None:
        super().__init__()
        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=settings.kafka.bootstrap_servers,
            group_id=settings.kafka.group_id,
            enable_auto_commit=False,
            auto_offset_reset=settings.kafka.auto_offset_reset,
        )

    async def start(self) -> None:
        await self._consumer.start()
        self._ready.set()

    async def stop(self) -> None:
        if self._closed:
            return
        
        self._closed = True
        self._ready.clear()
        await self._consumer.stop()

    async def consume(self, timeout: Optional[float] = 10.0) -> Message:
        try:
            await asyncio.wait_for(self._ready.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise RuntimeError("Consumer channel not ready")

        if self._closed:
            raise RuntimeError("Consumer channel is closed")

        record = await self._consumer.getone()

        return Message(
            topic=record.topic,
            partition=record.partition,
            offset=record.offset,
            key=record.key,
            value=record.value,
            headers=record.headers,
            timestamp=record.timestamp,
        )

    async def consume_batch(self, max_records: int, timeout: int) -> List[Message]:
        if self._closed:
            raise RuntimeError("Consumer channel is closed")

        records = await self._consumer.getmany(
            timeout_ms=timeout, max_records=max_records
        )

        messages = []
        for tp, records_l in records.items():
            for record in records_l:
                messages.append(
                    Message(
                        topic=record.topic,
                        partition=record.partition,
                        offset=record.offset,
                        key=record.key,
                        value=record.value,
                        headers=record.headers,
                        timestamp=record.timestamp,
                    )
                )
        return messages

    def subscribe(self, topics: Iterable[str]) -> None:
        self._consumer.subscribe(topics=topics)

    async def commit_offsets(self, offsets: Mapping[TP, int]) -> None:
        if self._closed:
            return

        if not offsets:
            await self._consumer.commit()
            return

        kafka_offsets = {
            TopicPartition(tp.topic, tp.partition): offset
            for tp, offset in offsets.items()
        }

        await self._consumer.commit(kafka_offsets)
