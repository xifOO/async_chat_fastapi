from pydantic import BaseModel


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: str


class PermissionCreate(PermissionBase): ...


class PermissionUpdate(PermissionBase): ...
