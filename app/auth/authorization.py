from datetime import UTC, datetime, timedelta
from typing import List, Optional, Union

import jwt
from fastapi import HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import ValidationError

from app.config import settings
from app.enum import TokenType
from app.models.models import User
from app.schemas.auth import AccessTokenResponse, JwtPayload, RefreshTokenResponse
from app.schemas.user import UserSchema


class AuthJWT:
    def __init__(self, request: Request) -> None:
        self.request = request

    def _create_payload(
        self,
        sub: Union[str, int],
        token_type: str,
        username: str,
        email: str,
        roles: List[str],
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

    def _create_token(self, payload: JwtPayload) -> str:
        token = jwt.encode(
            payload=payload.model_dump(),
            key=settings.auth.secret_key,
            algorithm=settings.auth.algorithm,
        )
        return token

    def create_access_token(self, user: User) -> AccessTokenResponse:
        payload = self._create_payload(
            user.id,
            token_type=TokenType.ACCESS,
            username=user.username,
            email=user.email,
            roles=user.roles,
        )
        token = self._create_token(payload)
        return AccessTokenResponse(access_token=token)

    def create_refresh_token(self, user: User) -> RefreshTokenResponse:
        payload = self._create_payload(
            user.id,
            token_type=TokenType.REFRESH,
            username=user.username,
            email=user.email,
            roles=user.roles,
        )
        token = self._create_token(payload)
        return RefreshTokenResponse(refresh_token=token)

    def verify_token(self, token: str) -> JwtPayload:
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

    def get_token_from_cookie(self, cookie_name: str) -> Optional[str]:
        return self.request.cookies.get(cookie_name)

    def get_token_from_header(self) -> Optional[str]:
        auth_header = self.request.headers.get("Authorization")
        if auth_header:
            scheme, token = get_authorization_scheme_param(auth_header)
            if scheme.lower() == TokenType.BEARER:
                return token
        return None

    def get_current_user(self) -> UserSchema:
        token = self.get_token_from_header()

        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        payload = self.verify_token(token)

        if payload.type != TokenType.ACCESS:
            raise HTTPException(status_code=401, detail="Invalid token type")

        return UserSchema(
            id=int(payload.sub),
            username=payload.username,
            email=payload.email,
            roles=payload.roles,
        )
