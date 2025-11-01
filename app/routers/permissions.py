from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from app.exceptions import RecordAlreadyExists, RecordNotFound
from app.permissions.decorators import check_permission, check_role, requires_check
from app.routers.roles import RoleServiceDep
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
    permission_data: PermissionCreate, service: PermissionServiceDep
):
    try:
        permission = await service.create(permission_data)
        return permission
    except RecordAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e.detail))


@router.post("/{permission_id}/roles/{role_id}", status_code=204)
@requires_check(check_role("admin"))
async def assign_role_to_permission(
    permission_id: int,
    role_id: int,
    perm_service: PermissionServiceDep,
    role_service: RoleServiceDep,
):
    try:
        permission = await perm_service.find_one(id=permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        role = await role_service.find_one(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        await perm_service.assing_to_role(permission_id, role_id)

    except RecordAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e.detail))
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=str(e.detail))
