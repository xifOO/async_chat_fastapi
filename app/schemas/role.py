from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.base import ResponseMixin


class RoleBase(BaseModel):
    name: str
    description: str

    @field_validator("name", "description", mode="before")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Fields can't be empty")
        return value


class RoleCreate(RoleBase): ...


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name", "description", mode="before")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        if value is not None and not value.strip():
            raise ValueError("Fields can't be empty")
        return value


class RoleResponse(RoleBase, ResponseMixin):
    id: int
