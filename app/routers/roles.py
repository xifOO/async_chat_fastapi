from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from app.exceptions import RecordAlreadyExists, RecordNotFound
from app.permissions.decorators import check_permission, check_role, requires_check
from app.routers.users import UserServiceDep
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
async def create_role(role_data: RoleCreate, service: RoleServiceDep):
    try:
        role = await service.create(role_data)
        return role
    except RecordAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e.detail))


@router.post("/{role_id}/users/{user_id}", status_code=204)
@requires_check(check_role("admin"))
async def assign_role_to_user(
    role_id: int,
    user_id: int,
    role_service: RoleServiceDep,
    user_service: UserServiceDep,
):
    try:
        user = await user_service.find_one(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role = await role_service.find_one(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        await role_service.assign_to_user(role_id, user_id)
    except RecordAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e.detail))
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=str(e.detail))
