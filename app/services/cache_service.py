import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis()
        value = await r.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Cache GET failed for key {key}: {e}")
    return None


async def cache_set(key: str, value: Any, ttl: int) -> bool:
    try:
        r = await get_redis()
        serialized = json.dumps(value, default=str)
        await r.setex(key, ttl, serialized)
        return True
    except Exception as e:
        logger.warning(f"Cache SET failed for key {key}: {e}")
    return False


async def cache_delete(key: str) -> bool:
    try:
        r = await get_redis()
        await r.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache DELETE failed for key {key}: {e}")
    return False


async def cache_invalidate_pattern(pattern: str) -> int:
    try:
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            return await r.delete(*keys)
    except Exception as e:
        logger.warning(f"Cache invalidate failed for pattern {pattern}: {e}")
    return 0


def make_search_key(query: str, category: Optional[str] = None) -> str:
    q = query.lower().strip().replace(" ", "_")
    return f"search:{q}:{category or 'all'}"


def make_deals_key(category: Optional[str] = None, page: int = 1) -> str:
    return f"deals:{category or 'all'}:p{page}"


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
