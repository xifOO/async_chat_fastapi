from pydantic import BaseModel, field_validator


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: str

    @field_validator("name", "resource", "action", mode="before")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Fields can't be empty")
        return value


class PermissionCreate(PermissionBase): ...


class PermissionUpdate(PermissionBase): ...


class PermissionResponse(PermissionBase):
    id: int
