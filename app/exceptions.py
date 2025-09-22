from typing import Any

from fastapi import HTTPException


class RecordAlreadyExists(HTTPException):
    def __init__(self, status_code: int, detail: Any = None) -> None:
        super().__init__(status_code, detail)
