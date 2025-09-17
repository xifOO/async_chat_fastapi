from typing import List

from fastapi import APIRouter

from app.schemas.role import RoleBase, RoleCreate
from app.schemas.user_role import UserToRoleBase, UserToRoleCreate
from app.services.role import RoleService
from app.services.user_role import UserToRoleService

router = APIRouter(prefix="/role", tags=["Role"])


@router.get("/", response_model=List[RoleBase])
async def get_roles():
    roles = await RoleService().find_all()
    return roles


@router.post("/create", response_model=RoleBase)
async def create_role(role_data: RoleCreate):
    role = await RoleService().create(role_data)
    return role


@router.post("/assign", response_model=UserToRoleBase)
async def assign_role_to_user(user_to_role_data: UserToRoleCreate):
    user_to_role = await UserToRoleService().create(user_to_role_data)
    return user_to_role
