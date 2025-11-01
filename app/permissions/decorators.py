from functools import wraps
from typing import Awaitable, Callable, Optional

from fastapi import HTTPException
from pydantic import BaseModel

from app.middleware.context import current_request, current_user


def requires_check(check: Optional[Callable[[dict], Awaitable[bool]]] = None):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = current_user.get()

            if not user or not user.is_authenticated:
                raise HTTPException(status_code=403, detail="Permission denied")

            ok = True
            if check:
                ok = await check(kwargs)

            if not ok:
                raise HTTPException(status_code=403, detail="Permission denied")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_role(*roles: str):
    async def _check(kwargs) -> bool:
        request = current_request.get()
        return (
            any(f"role:{role}" in request.auth.scopes for role in roles)
            if request
            else False
        )

    return _check


def check_permission(resource: str, action: str):
    async def _check(kwargs) -> bool:
        request = current_request.get()
        return f"perm:{resource}:{action}" in request.auth.scopes if request else False

    return _check


def check_own_or_permission(
    resource: str,
    action: str,
    owner_field: Optional[str] = None,
    get_object: Optional[Callable[[dict], Awaitable[Optional[dict]]]] = None,
):
    async def _check(kwargs: dict) -> bool:
        obj = None
        request = current_request.get()
        user = current_user.get()

        if not user:
            raise HTTPException(status_code=403, detail="Permission denied")

        if get_object:
            obj = await get_object(kwargs)

        author_id = None
        if obj:
            if isinstance(obj, BaseModel):
                obj_dict: dict = obj.model_dump()  # type: ignore
                author_id = str(obj_dict.get(owner_field))
            elif isinstance(obj, dict):
                author_id = str(obj.get(owner_field))

        if str(user.id) == str(author_id):
            return True

        return f"perm:{resource}:{action}" in request.auth.scopes if request else False

    return _check
