import redis.asyncio as redis
import json

from config import REDIS_SETTINGS


async def get_from_redis(hash_name: str):
    """
    Get from Redis "key:value" data
    Args:
        hash_name: str

    Returns:

    """
    redis_client = redis.Redis(**REDIS_SETTINGS)
    value = await redis_client.get(hash_name)
    await redis_client.aclose()
    return value


async def set_to_redis(hash_name: str, value: str, ex: int = 60):
    """
    Send to Redis "key:value" data with ex
    Args:
        hash_name: str
        value: str
        ex: int

    Returns:

    """
    redis_client = redis.Redis(**REDIS_SETTINGS)
    await redis_client.set(hash_name, value, ex=ex)
    await redis_client.aclose()
