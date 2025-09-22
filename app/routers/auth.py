from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.authorization import create_access_token, create_refresh_token
from app.auth.cookie import set_refresh_cookie
from app.permissions import requires_authenticated, requires_role
from app.schemas.auth import AccessTokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.users import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=UserResponse)
@requires_authenticated()
async def get_user_profile(request: Request):
    user_profile = await UserService().get_user_profile(request.user)
    return user_profile


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    user = await UserService().register_user(user_data)
    return user


@router.post("/login", response_model=AccessTokenResponse)
async def login(
    response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await UserService().authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user).access_token
    refresh_token = create_refresh_token(user).refresh_token

    set_refresh_cookie(response, refresh_token)

    return AccessTokenResponse(access_token=access_token)


@router.delete("/delete/{user_id}", status_code=204)
@requires_role("admin")
async def delete_user(request: Request, user_id: int):
    await UserService().delete(user_id)
