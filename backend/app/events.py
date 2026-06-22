import json

import redis.asyncio as redis

from .config import settings

_redis: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def publish_event(event: dict) -> None:
    r = await get_redis()
    await r.publish(settings.EVENTS_CHANNEL, json.dumps(event, default=str))


async def enqueue_job(job: dict) -> None:
    r = await get_redis()
    await r.lpush(settings.QUEUE_NAME, json.dumps(job, default=str))
