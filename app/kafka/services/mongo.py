from app.kafka.serializers import JSONCodec
from app.kafka.transport import Transport
from app.schemas.message import MessageCreate
from app.services.message import MessageService
from app.types.message import Headers
from app.types.transport import ServiceT


class KafkaToMongoDB(ServiceT):
    def __init__(self, topic: str, headers: Headers) -> None:
        self.topic = topic
        self.headers = headers
        self.transport = Transport()
        self.mongo = MessageService()
        self.consumer = None
        super().__init__()

    async def start(self) -> None:
        if not self._closed:
            return

        self.consumer = self.transport.create_consumer()
        self.consumer.subscribe([self.topic])
        await self.consumer.start()

        self._closed = False
        self._ready.set()

    async def stop(self) -> None:
        if self._closed:
            return

        if self.consumer:
            try:
                await self.consumer.commit()
            except Exception:
                pass
            await self.consumer.close()

        self._ready.clear()
        self._closed = True

    async def process(self) -> None:
        if self._closed or not self._ready.is_set():
            return

        if not self.consumer:
            return

        messages = await self.consumer.consume_batch(max_records=100, timeout=10)

        for message in messages:
            if message.value:
                json_data = JSONCodec().loads(message.value) # later: change (serialize up level or object)
                message = MessageCreate(**json_data)
                await self.mongo.create(message)

        await self.consumer.commit()
