from fastapi import APIRouter

from app.dependencies import UOWDep
from app.schemas.role import RoleBase, RoleCreate
from app.schemas.user_role import UserToRoleBase, UserToRoleCreate
from app.services.role import RoleService
from app.services.user_role import UserToRoleService

router = APIRouter(prefix="/role", tags=["Role"])


@router.post("/create", response_model=RoleBase)
async def create_role(uow: UOWDep, role_data: RoleCreate):
    role = await RoleService(uow).create_role(role_data)
    return role


@router.post("/assing", response_model=UserToRoleBase)
async def assing_role_to_user(uow: UOWDep, user_to_role_data: UserToRoleCreate):
    user_to_role = await UserToRoleService(uow).assing_role_to_user(user_to_role_data)
    return user_to_role