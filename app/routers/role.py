from typing import List

from fastapi import APIRouter, Request

from app.permissions import requires_permission, requires_role
from app.schemas.role import RoleCreate, RoleResponse
from app.schemas.user_role import UserToRoleBase, UserToRoleCreate
from app.services.role import RoleService
from app.services.user_role import UserToRoleService

router = APIRouter(prefix="/role", tags=["Role"])


@router.get("/", response_model=List[RoleResponse])
async def get_roles():
    roles = await RoleService().find_all()
    return roles


@router.post("/create", response_model=RoleResponse)
@requires_permission("role", "create")
async def create_role(request: Request, role_data: RoleCreate):
    role = await RoleService().create(role_data)
    return role


@router.post("/assign", response_model=UserToRoleBase)
@requires_role("admin")
async def assign_role_to_user(request: Request, user_to_role_data: UserToRoleCreate):
    user_to_role = await UserToRoleService().create(user_to_role_data)
    return user_to_role
