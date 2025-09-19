from functools import wraps
from typing import Callable, Optional

from fastapi import HTTPException, Request
from starlette.authentication import requires


def requires_authenticated(permissions: Optional[list[str]] = None):
    if permissions is None:
        permissions = []

    def decorator(func: Callable) -> Callable:
        requires_decorated = requires(["authenticated"] + permissions)(func)

        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise HTTPException(status_code=401, detail="Authentication required")
            return await requires_decorated(request, *args, **kwargs)

        return wrapper

    return decorator


def requires_permission(resource: str, action: str):
    return requires_authenticated([f"perm:{resource}:{action}"])


def requires_role(role: str):
    return requires_authenticated([f"role:{role}"])


def requires_any_role(*roles: str):
    return requires_authenticated([*[f"role:{role}" for role in roles]])
