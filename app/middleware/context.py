from contextvars import ContextVar
from typing import TYPE_CHECKING, Awaitable, Callable, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

if TYPE_CHECKING:
    from app.middleware.auth_middleware import _AuthenticatedUser


current_user: ContextVar[Optional["_AuthenticatedUser"]] = ContextVar(
    "current_user", default=None
)
current_request: ContextVar[Optional[Request]] = ContextVar(
    "current_request", default=None
)


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        current_request.set(request)
        current_user.set(None)
        response = await call_next(request)
        return response
