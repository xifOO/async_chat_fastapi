import re
from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.role import RoleBase


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

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


class UserInDB(UserBase):
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(UserBase): ...


class UserSchema(UserBase):
    id: int
    roles: List[RoleBase]


class UserProfile(UserSchema):
    created_at: datetime
    updated_at: datetime
