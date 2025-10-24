from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class CodecT(ABC):
    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    def dumps(self, obj: Any) -> bytes: ...

    @abstractmethod
    def loads(self, s: bytes) -> Any: ...


CodecArg = Optional[Union[CodecT, str]]
