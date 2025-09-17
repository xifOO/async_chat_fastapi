from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.auth.authorization import create_access_token, create_refresh_token
from app.auth.cookie import set_refresh_cookie
from app.schemas.auth import AccessTokenResponse
from app.schemas.user import UserBase, UserCreate, UserResponse, UserSchema
from app.services.users import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(request: Request) -> UserSchema:
    user = request.user
    if not user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.user


@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    user: Annotated[UserSchema, Depends(get_current_user)],
    token: Annotated[str, Depends(oauth2_scheme)],
):  # token for swagger :)
    user_profile = await UserService().get_user_profile(user)
    return user_profile


@router.post("/register", response_model=UserBase)
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
