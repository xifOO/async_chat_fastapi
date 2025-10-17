import json
from typing import Any

from pydantic import BaseModel

from app.types.codecs import CodecArg, CodecT


class JSONCodec(CodecT):
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def dumps(self, obj: Any) -> bytes:
        if obj is None:
            return b""
        if isinstance(obj, BaseModel):
            return obj.model_dump_json().encode(self.encoding)
        if isinstance(obj, str):
            return obj.encode(self.encoding)
        return json.dumps(obj).encode(self.encoding)

    def loads(self, s: bytes) -> Any:
        if not s:
            return None
        return json.loads(s.decode(self.encoding))


def serialize(value: Any, codec: CodecArg = None) -> bytes:
    if value is None:
        return b""

    if isinstance(codec, CodecT):
        return codec.dumps(value)

    if isinstance(codec, str) and codec.lower() == "json":
        return JSONCodec().dumps(value)

    if isinstance(value, BaseModel):
        return value.model_dump_json().encode("utf-8")

    if isinstance(value, str):
        return value.encode("utf-8")

    return json.dumps(value).encode("utf-8")
