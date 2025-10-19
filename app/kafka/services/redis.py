from app.cache import RedisManager
from app.kafka.transport import Transport
from app.types.transport import Headers, ServiceT


class RedisToKafkaService(ServiceT):
    def __init__(self, topic: str, partition: int, headers: Headers) -> None:
        self.topic = topic
        self.partition = partition
        self.headers = headers
        self.transport = Transport()
        self.redis = RedisManager()
        self.producer = None
        super().__init__()

    async def start(self) -> None:
        if not self._closed:
            return

        self.producer = self.transport.create_producer()
        await self.producer.start()
        await self.redis.connect()

        self._closed = True

    async def stop(self) -> None:
        if self._closed:
            return
        
        self._closed = True

        if self.producer:
            await self.producer.close()
        
        await self.redis.disconnect()

    async def process(self) -> None:
        if self.producer:
            messages = await self.redis.scan_all()
            for message in messages:
                
                if isinstance(message, dict):
                    conversation_id = message.get("conversationId")
                else:
                    conversation_id = getattr(message, "conversationId", None)

                await self.producer.send(
                    topic=self.topic,
                    key=conversation_id,
                    value=message, 
                    partition=self.partition,
                    headers=self.headers,
                )

            await self.producer.flush()
