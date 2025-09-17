from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str


class RoleCreate(RoleBase): ...


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
