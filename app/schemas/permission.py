from pydantic import BaseModel


class PermissionCreate(BaseModel):
    name: str
    resource: str
    action: str
    description: str


class PermissionUpdate(PermissionCreate): ...
