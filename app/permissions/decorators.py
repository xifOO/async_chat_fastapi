from functools import wraps
from typing import Awaitable, Callable, Optional

from fastapi import HTTPException, Request


def requires_check(check: Optional[Callable[[Request, dict], Awaitable[bool]]] = None):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            ok = True
            if check:
                ok = await check(request, kwargs)

            if not ok or not request.user.is_authenticated:
                raise HTTPException(status_code=403, detail="Permission denied")

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def check_role(*roles: str):
    async def _check(request: Request, kwargs) -> bool:
        return any(f"role:{role}" in request.auth.scopes for role in roles)

    return _check


def check_permission(resource: str, action: str):
    async def _check(request: Request, kwargs) -> bool:
        return f"perm:{resource}:{action}" in request.auth.scopes

    return _check


def check_own_or_permission(
    resource: str,
    action: str,
    owner_field: Optional[str] = None,
    get_object: Optional[Callable[[Request, dict], Awaitable[Optional[dict]]]] = None,
):
    async def _check(request: Request, kwargs: dict) -> bool:
        obj = None
        if get_object:
            obj = await get_object(request, kwargs)

        author_id = None
        if obj:
            obj_dict: dict = obj.model_dump()  # type: ignore
            author_id = str(obj_dict.get(owner_field))

        if str(request.user.id) == str(author_id):
            return True

        return f"perm:{resource}:{action}" in request.auth.scopes

    return _check
