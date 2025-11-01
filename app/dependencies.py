from typing import Annotated

from fastapi import Depends

from app.cache import RedisManager

redis_manager = RedisManager()


def get_redis_manager() -> RedisManager:
    return redis_manager


RedisManagerDep = Annotated[RedisManager, Depends(get_redis_manager)]
