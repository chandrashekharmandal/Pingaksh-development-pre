"""
Core Redis client module.

Provides connection pools for the three Redis databases:
- DB 0: Cache, sessions, real-time state (guard location, online status, OTP, rate limits)
- DB 1: Celery broker and results
- DB 2: Django Channels layer

Usage:
    from apps.core.redis_client import get_redis
    r = get_redis()
    r.set("key", "value", ex=300)
"""

import redis
from django.conf import settings


def _get_redis_url(db: int = 0) -> str:
    """Get Redis URL for the given DB number."""
    base_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
    # Replace the DB number in the URL
    if base_url.endswith(f"/{db}"):
        return base_url
    # Strip trailing /N and append correct DB
    parts = base_url.rsplit("/", 1)
    if parts[-1].isdigit():
        return f"{parts[0]}/{db}"
    return f"{base_url}/{db}"


# Lazy connection pool initialization
_pool_db0 = None
_pool_db2 = None


def _get_pool_db0():
    global _pool_db0
    if _pool_db0 is None:
        _pool_db0 = redis.ConnectionPool.from_url(
            _get_redis_url(0),
            max_connections=50,
            socket_connect_timeout=5,
            socket_timeout=5,
            decode_responses=True,
        )
    return _pool_db0


def _get_pool_db2():
    global _pool_db2
    if _pool_db2 is None:
        url = getattr(settings, "REDIS_CHANNELS_URL", _get_redis_url(2))
        _pool_db2 = redis.ConnectionPool.from_url(
            url,
            max_connections=20,
            decode_responses=True,
        )
    return _pool_db2


def get_redis() -> redis.Redis:
    """Return a Redis client for DB 0 (cache / real-time state)."""
    return redis.Redis(connection_pool=_get_pool_db0())


def get_channels_redis() -> redis.Redis:
    """Return a Redis client for DB 2 (Channels layer inspection)."""
    return redis.Redis(connection_pool=_get_pool_db2())
