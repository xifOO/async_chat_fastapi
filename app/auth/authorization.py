from datetime import datetime, timedelta, timezone
from typing import List, Union

import jwt
from fastapi import HTTPException
from pydantic import ValidationError

from app.config import settings
from app.enum import TokenType
from app.models.models import Role, User
from app.schemas.auth import AccessTokenResponse, JwtPayload, RefreshTokenResponse
from app.schemas.user import UserSchema


def _create_payload(
    sub: Union[str, int],
    token_type: str,
    username: str,
    email: str,
    roles: List[Role],
) -> JwtPayload:
    if token_type == TokenType.ACCESS:
        token_expires_minutes = settings.auth.access_token_expires_minutes
    elif token_type == TokenType.REFRESH:
        token_expires_minutes = settings.auth.refresh_token_expires_minutes
    else:
        raise ValueError(f"Unknown token type: {token_type}")

    exp = datetime.now(timezone.utc) + timedelta(minutes=token_expires_minutes)
    role_names = [role.name for role in roles]

    payload = JwtPayload(
        sub=str(sub),
        exp=exp,
        iat=datetime.now(timezone.utc),
        aud=settings.auth.JWT_AUDIENCE,
        iss=settings.auth.JWT_ISSUER,
        type=token_type,
        username=username,
        email=email,
        roles=role_names,
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
            audience=settings.auth.JWT_AUDIENCE,
            issuer=settings.auth.JWT_ISSUER,
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
        roles=payload.roles,
    )
