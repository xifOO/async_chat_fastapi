from datetime import UTC, datetime, timedelta
from typing import List, Union

import jwt
from fastapi import HTTPException
from pydantic import ValidationError

from app.config import settings
from app.enum import TokenType
from app.models.models import User
from app.schemas.auth import AccessTokenResponse, JwtPayload, RefreshTokenResponse
from app.schemas.user import UserSchema


def _create_payload(
    sub: Union[str, int],
    token_type: str,
    username: str,
    email: str,
    roles: List[int],
) -> JwtPayload:
    if token_type == TokenType.ACCESS:
        token_expires_minutes = settings.auth.access_token_expires_minutes
    elif token_type == TokenType.REFRESH:
        token_expires_minutes = settings.auth.refresh_token_expires_minutes
    else:
        raise ValueError(f"Unknown token type: {token_type}")

    exp = datetime.now(UTC) + timedelta(minutes=token_expires_minutes)

    payload = JwtPayload(
        sub=str(sub),
        exp=exp,
        iat=datetime.now(UTC),
        type=token_type,
        username=username,
        email=email,
        roles=roles,
    )
    return payload


def _create_token(payload: JwtPayload) -> str:
    token = jwt.encode(
        payload=payload.model_dump(),
        key=settings.auth.secret_key,
        algorithm=settings.auth.algorithm,
    )
    return token


def create_access_token(user: User) -> AccessTokenResponse:
    payload = _create_payload(
        user.id,
        token_type=TokenType.ACCESS,
        username=user.username,
        email=user.email,
        roles=user.roles,
    )
    token = _create_token(payload)
    return AccessTokenResponse(access_token=token)


def create_refresh_token(user: User) -> RefreshTokenResponse:
    payload = _create_payload(
        user.id,
        token_type=TokenType.REFRESH,
        username=user.username,
        email=user.email,
        roles=user.roles,
    )
    token = _create_token(payload)
    return RefreshTokenResponse(refresh_token=token)


def _verify_token(token: str) -> JwtPayload:
    try:
        payload = jwt.decode(
            token,
            key=settings.auth.secret_key,
            algorithms=[settings.auth.algorithm],
        )
        return JwtPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValidationError:
        raise HTTPException(status_code=401, detail="Invalid token payload")


def get_current_user_from_token(token: str) -> UserSchema:
    payload = _verify_token(token)

    if payload.type != TokenType.ACCESS:
        raise HTTPException(status_code=401, detail="Invalid token type")

    return UserSchema(
        id=int(payload.sub),
        username=payload.username,
        email=payload.email,
        role_ids=payload.roles,
    )
