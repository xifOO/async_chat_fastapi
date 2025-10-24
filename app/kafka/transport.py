from typing import Any, ClassVar, Type

from app.kafka.consumers import Consumer
from app.kafka.producers import Producer
from app.types.transport import ConsumerT, ProducerT, TransportT


class Transport(TransportT):
    Consumer: ClassVar[Type[ConsumerT]] = Consumer
    Producer: ClassVar[Type[ProducerT]] = Producer

    def __init__(self) -> None:
        pass

    def create_consumer(self, **kwargs: Any) -> ConsumerT:
        return self.Consumer(**kwargs)

    def create_producer(self, **kwargs: Any) -> ProducerT:
        return self.Producer(**kwargs)
