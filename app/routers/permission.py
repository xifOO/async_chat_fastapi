from fastapi import APIRouter

from app.schemas.permission import PermissionBase, PermissionCreate
from app.schemas.role_permission import RoleToPermissionBase, RoleToPermissionCreate
from app.services.permission import PermissionService
from app.services.role_permission import RoleToPermissionService

router = APIRouter(prefix="/permission", tags=["Permission"])


@router.post("/create", response_model=PermissionBase)
async def create_permission(permission_data: PermissionCreate):
    permission = await PermissionService().create(permission_data)
    return permission


@router.post("/assign", response_model=RoleToPermissionBase)
async def assign_role_to_permission(role_to_permission_data: RoleToPermissionCreate):
    role_to_permission = await RoleToPermissionService().create(role_to_permission_data)
    return role_to_permission
