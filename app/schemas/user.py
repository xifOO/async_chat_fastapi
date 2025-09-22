import re
import sys
from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, field_validator, model_validator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    password_repeat: str

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: str) -> str:
        pattern_password = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^\w\s]).{6,}"
        )
        if bool(pattern_password.match(value)):
            return value
        else:
            raise ValueError("You have entered an invalid password")

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Username can't be empty")
        if len(value) < 4:
            raise ValueError("Username must be at least 4 characters long")
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match")
        return self


class UserInDB(UserBase):
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(UserBase): ...


class UserSchema(UserBase):
    id: int
    roles: List[str]


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
