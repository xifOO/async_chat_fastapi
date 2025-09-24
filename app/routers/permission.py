from typing import List

from fastapi import APIRouter, Request

from app.permissions import check_permission, check_role, requires_check
from app.schemas.permission import PermissionCreate, PermissionResponse
from app.schemas.role_permission import RoleToPermissionBase, RoleToPermissionCreate
from app.services.permission import PermissionService
from app.services.role_permission import RoleToPermissionService

router = APIRouter(prefix="/permission", tags=["Permission"])


@router.get("/", response_model=List[PermissionResponse])
async def get_permissions():
    permissions = await PermissionService().find_all()
    return permissions


@router.post("/create", response_model=PermissionResponse)
@requires_check(check_permission("permission", "create"))
async def create_permission(request: Request, permission_data: PermissionCreate):
    permission = await PermissionService().create(permission_data)
    return permission


@router.post("/assign", response_model=RoleToPermissionBase)
@requires_check(check_role("admin"))
async def assign_role_to_permission(
    request: Request, role_to_permission_data: RoleToPermissionCreate
):
    role_to_permission = await RoleToPermissionService().create(role_to_permission_data)
    return role_to_permission
