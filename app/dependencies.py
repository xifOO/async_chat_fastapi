from typing import Annotated

from fastapi import Depends

from app.aws import AWSManager
from app.cache import RedisManager

redis_manager = RedisManager()


def get_redis_manager() -> RedisManager:
    return redis_manager


async def get_aws_manager() -> AWSManager:
    return AWSManager()


RedisManagerDep = Annotated[RedisManager, Depends(get_redis_manager)]
AWSManagerDep = Annotated[AWSManager, Depends(get_aws_manager)]
