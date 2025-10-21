from app.cache import RedisManager
from app.kafka.transport import Transport
from app.types.message import Headers
from app.types.transport import ServiceT


class RedisToKafkaService(ServiceT):
    def __init__(self, topic: str, headers: Headers) -> None:
        self.topic = topic
        self.headers = headers
        self.transport = Transport()
        self.redis = RedisManager()
        self.producer = None
        self._cursor = 0
        super().__init__()

    async def start(self) -> None:
        if not self._closed:
            return

        self.producer = self.transport.create_producer()
        await self.producer.start()
        await self.redis.connect()

        self._closed = False
        self._ready.set() 

    async def stop(self) -> None:
        if self._closed:
            return

        if self.producer:
            await self.producer.close()
        
        await self.redis.disconnect()
        self._ready.clear()
        self._closed = True

    async def process(self) -> None:
        if self._closed or not self._ready.is_set():
            return

        if not self.producer:
            return

        self._cursor, chat_keys = await self.redis.get_batch(
            cursor=self._cursor,
            count=10
        )

        if not chat_keys:
            self._cursor = 0
            return 

        for chat_key in chat_keys:
            messages = await self.redis.pop_messages(
                chat_key,
                batch_size=100
            )
            for message in messages:
                await self.producer.send(
                    topic=self.topic,
                    key=message.get("conversationId"),
                    value=message, 
                    headers=self.headers
                )

        await self.producer.flush()
