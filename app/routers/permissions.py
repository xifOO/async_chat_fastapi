from typing import Annotated, List

from fastapi import APIRouter, Depends, Request

from app.permissions import check_permission, check_role, requires_check
from app.schemas.permission import PermissionCreate, PermissionResponse
from app.services.permission import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"])


def get_permission_service() -> PermissionService:
    return PermissionService()


PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]


@router.get("/", response_model=List[PermissionResponse])
async def get_permissions(service: PermissionServiceDep):
    permissions = await service.find_all()
    return permissions


@router.post("/", response_model=PermissionResponse, status_code=201)
@requires_check(check_permission("permission", "create"))
async def create_permission(
    request: Request, permission_data: PermissionCreate, service: PermissionServiceDep
):
    permission = await service.create(permission_data)
    return permission


@router.post("/{permission_id}/roles/{role_id}", status_code=204)
@requires_check(check_role("admin"))
async def assign_role_to_permission(
    request: Request, permission_id: int, role_id: int, service: PermissionServiceDep
):
    await service.assing_to_role(permission_id, role_id)
