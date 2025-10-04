from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.authorization import create_access_token, create_refresh_token
from app.auth.cookie import set_refresh_cookie
from app.routers.users import UserServiceDep
from app.schemas.auth import AccessTokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sessions", response_model=AccessTokenResponse)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserServiceDep,
):
    user = await service.authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user).access_token
    refresh_token = create_refresh_token(user).refresh_token

    set_refresh_cookie(response, refresh_token)

    return AccessTokenResponse(access_token=access_token)


# logout, refresh in next time
