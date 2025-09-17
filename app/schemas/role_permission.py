from pydantic import BaseModel


class RoleToPermissionBase(BaseModel):
    role_id: int
    permission_id: int


class RoleToPermissionCreate(RoleToPermissionBase): ...


class RoleToPermissionUpdate(RoleToPermissionBase): ...
