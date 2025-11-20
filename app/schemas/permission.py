from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.base import ResponseMixin


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None

    @field_validator("name", "resource", "action", "description", mode="before")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Fields can't be empty")
        return value


class PermissionCreate(PermissionBase): ...


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name", "resource", "action", mode="before")
    @classmethod
    def validate_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("Fields can't be empty")
        return value


class PermissionResponse(PermissionBase, ResponseMixin):
    id: int
