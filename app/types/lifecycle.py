from abc import ABC, abstractmethod
import asyncio


class LifecycleT(ABC):
    def __init__(self) -> None:
        self._closed = False
        self._ready = asyncio.Event()

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...
