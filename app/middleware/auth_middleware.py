import re
from typing import Mapping, Optional, Tuple

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.requests import HTTPConnection

from app.auth.authorization import get_current_user_from_token
from app.config import settings
from app.enum import TokenType
from app.schemas.user import UserSchema
from app.services.role import RoleService


class _AuthenticationError(AuthenticationError):
    def __init__(
        self,
        *,
        code: Optional[int] = None,
        msg: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.code = code
        self.msg = msg
        self.headers = headers


class _AuthenticatedUser(BaseUser):
    def __init__(self, user: UserSchema) -> None:
        self._user = user

    @property
    def is_authenticated(self) -> bool:
        return True
    
    @property
    def user(self) -> UserSchema:
        return self._user
    
    def __getattr__(self, name: str):
        return getattr(self._user, name)

class JWTAuthMiddleware(AuthenticationBackend):
    @staticmethod
    def auth_exception_handler(
        conn: HTTPConnection, exc: _AuthenticationError
    ) -> Response:
        return JSONResponse(
            content={"code": exc.code, "msg": exc.msg, "data": None},
            status_code=exc.code or 401,
        )

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        request = Request(conn.scope)

        path = request.url.path
        if path in settings.auth.TOKEN_REQUEST_PATH_EXCLUDE:
            return None

        for pattern_str in settings.auth.TOKEN_REQUEST_PATH_EXCLUDE_PATTERN:
            pattern = re.compile(pattern_str)
            if pattern.match(path):
                return None

        auth_header = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(auth_header)
        if not token:
            return None
        if scheme.lower() != TokenType.BEARER:
            raise _AuthenticationError(code=401, msg="Invalid authorization scheme")

        try:
            user = get_current_user_from_token(token)
            permissions = []
            roles = await RoleService().find_multiple_with_permissions(
                user.roles
            )  # later cache
            for role in roles:
                permissions.extend(role.permissions)

            credentials = [
                "authenticated",
                *[f"role:{role}" for role in user.roles],
                *[f"perm:{perm.resource}:{perm.action}" for perm in permissions],
            ]
        except HTTPException as exc:
            raise _AuthenticationError(code=exc.status_code, msg=exc.detail)
        except Exception as exc:
            raise _AuthenticationError(code=500, msg=str(exc))
        return AuthCredentials(credentials), _AuthenticatedUser(user)
