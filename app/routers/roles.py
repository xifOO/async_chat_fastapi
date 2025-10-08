from typing import Annotated, List

from fastapi import APIRouter, Depends, Request

from app.permissions.decorators import check_permission, check_role, requires_check
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role_service() -> RoleService:
    return RoleService()


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]


@router.get("/", response_model=List[RoleResponse])
async def get_roles(service: RoleServiceDep):
    roles = await service.find_all()
    return roles


@router.post("/", response_model=RoleResponse, status_code=201)
@requires_check(check_permission("role", "create"))
async def create_role(request: Request, role_data: RoleCreate, service: RoleServiceDep):
    role = await service.create(role_data)
    return role


@router.post("/{role_id}/users/{user_id}", status_code=204)
@requires_check(check_role("admin"))
async def assign_role_to_user(
    request: Request, role_id: int, user_id: int, service: RoleServiceDep
):
    await service.assign_to_user(role_id, user_id)
