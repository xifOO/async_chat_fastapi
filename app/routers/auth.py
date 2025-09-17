from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.auth.authorization import AuthJWT
from app.auth.cookie import set_refresh_cookie
from app.dependencies import UOWDep
from app.schemas.auth import AccessTokenResponse
from app.schemas.user import UserCreate, UserProfile, UserSchema
from app.services.users import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_jwt(request: Request):
    return AuthJWT(request)


async def get_current_user(
    auth: Annotated[AuthJWT, Depends(get_auth_jwt)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserSchema:  # token for swagger
    return auth.get_current_user()


@router.get("/me", response_model=UserProfile)
async def get_user_profile(uow: UOWDep, user: Annotated[UserSchema, Depends(get_current_user)]):
    user_profile = await UserService(uow).get_user_profile(user)
    return user_profile


@router.post("/register", response_model=UserSchema)
async def register_user(user_data: UserCreate, uow: UOWDep):
    user = await UserService(uow).register_user(user_data)
    return user


@router.post("/login", response_model=AccessTokenResponse)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: UOWDep,
    auth: Annotated[AuthJWT, Depends(get_auth_jwt)],
):
    user = await UserService(uow).authenticate_user(
        form_data.username, form_data.password
    )
    access_token = auth.create_access_token(user).access_token
    refresh_token = auth.create_refresh_token(user).refresh_token

    set_refresh_cookie(response, refresh_token)

    return AccessTokenResponse(access_token=access_token)
