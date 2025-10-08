from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.permissions.decorators import (
    check_own_or_permission,
    check_role,
    requires_check,
)
from app.permissions.getters import get_user
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service() -> UserService:
    return UserService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post("/", response_model=UserResponse, status_code=201)
async def register_user(user_data: UserCreate, service: UserServiceDep):
    user = await service.register_user(user_data)
    return user


@router.get("/me", response_model=UserResponse)
@requires_check()
async def get_user_profile(request: Request, service: UserServiceDep):
    user_profile = await service.get_user_profile(request.user)
    return user_profile


@router.delete("/{user_id}", status_code=204)
@requires_check(check_role("admin"))
async def delete_user(request: Request, user_id: int, service: UserServiceDep):
    await service.delete(user_id)
    return Response(status_code=204)


@router.patch("/{user_id}", response_model=UserResponse)
@requires_check(check_own_or_permission("update", "user", get_object=get_user))
async def update_user(
    request: Request, user_id: int, update_data: UserUpdate, service: UserServiceDep
):
    update_user = await service.update(user_id, update_data)
    return update_user
