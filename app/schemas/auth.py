from datetime import datetime
from typing import List, Union

from pydantic import BaseModel, EmailStr, field_validator

from app.enum import TokenType


class JwtPayload(BaseModel):
    sub: str
    exp: Union[int, datetime]
    iat: Union[int, datetime]
    type: str
    username: str
    email: EmailStr
    roles: List[int]

    @field_validator("exp", "iat", mode="before")
    @classmethod
    def convert_datetime_to_int(cls, value):
        if isinstance(value, datetime):
            return int(value.timestamp())
        return value


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = TokenType.BEARER


class RefreshTokenResponse(BaseModel):
    refresh_token: str
    token_type: str = TokenType.BEARER
