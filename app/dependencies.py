from app.cache import RedisManager


redis_manager = RedisManager()

def get_redis_manager() -> RedisManager:
    return redis_manager