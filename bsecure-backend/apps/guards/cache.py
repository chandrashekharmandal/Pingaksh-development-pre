"""
Guard profile and nearby results caching via Django cache framework.

Keys:
- bsecure:cache:guard:{guard_id} — cached guard profile (TTL=300s)
- bsecure:cache:user:{user_id} — cached user profile (TTL=300s)
- bsecure:cache:nearby:{lat}:{lon}:{radius} — cached nearby guards (TTL=30s)
"""

from django.core.cache import cache


GUARD_PROFILE_TTL = 300  # 5 minutes
USER_PROFILE_TTL = 300  # 5 minutes
NEARBY_RESULT_TTL = 30  # 30 seconds — location data changes fast


# ─── Guard Profile Cache ─────────────────────────────────────────────────────


def get_guard_profile_cache(guard_id: int) -> dict | None:
    key = f"bsecure:cache:guard:{guard_id}"
    return cache.get(key)


def set_guard_profile_cache(guard_id: int, data: dict):
    key = f"bsecure:cache:guard:{guard_id}"
    cache.set(key, data, timeout=GUARD_PROFILE_TTL)


def invalidate_guard_profile_cache(guard_id: int):
    cache.delete(f"bsecure:cache:guard:{guard_id}")


# ─── User Profile Cache ──────────────────────────────────────────────────────


def get_user_profile_cache(user_id: int) -> dict | None:
    key = f"bsecure:cache:user:{user_id}"
    return cache.get(key)


def set_user_profile_cache(user_id: int, data: dict):
    key = f"bsecure:cache:user:{user_id}"
    cache.set(key, data, timeout=USER_PROFILE_TTL)


def invalidate_user_profile_cache(user_id: int):
    cache.delete(f"bsecure:cache:user:{user_id}")


# ─── Nearby Guards Cache ─────────────────────────────────────────────────────


def get_nearby_cache_key(lat: float, lon: float, radius: int) -> str:
    """Round coordinates to 3 decimal places (~111m) to improve hit rate."""
    return f"bsecure:cache:nearby:{round(lat, 3)}:{round(lon, 3)}:{radius}"


def get_nearby_guards_cache(lat: float, lon: float, radius: int) -> list | None:
    key = get_nearby_cache_key(lat, lon, radius)
    return cache.get(key)


def set_nearby_guards_cache(lat: float, lon: float, radius: int, data: list):
    key = get_nearby_cache_key(lat, lon, radius)
    cache.set(key, data, timeout=NEARBY_RESULT_TTL)
