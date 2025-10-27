import asyncio
from abc import ABC, abstractmethod


class LifecycleT(ABC):
    def __init__(self) -> None:
        self._closed = True
        self._ready = asyncio.Event()

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...
