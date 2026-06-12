"""
Guard real-time location tracking via Redis.

Key: bsecure:location:guard:{guard_id} (Hash, TTL=300s)
Fields: lat, lon, heading, speed, updated_at, booking_id
"""

from django.utils import timezone

from apps.core.redis_client import get_redis


LOCATION_TTL = 300  # 5 minutes — guard considered offline if not refreshed


def update_guard_location(
    guard_id: int,
    lat: float,
    lon: float,
    heading: float = 0.0,
    speed: float = 0.0,
    booking_id: int = None,
):
    """Update guard's real-time location in Redis. Resets TTL on every call."""
    r = get_redis()
    key = f"bsecure:location:guard:{guard_id}"

    r.hset(
        key,
        mapping={
            "lat": str(lat),
            "lon": str(lon),
            "heading": str(heading),
            "speed": str(speed),
            "updated_at": timezone.now().isoformat(),
            "booking_id": str(booking_id) if booking_id else "",
        },
    )
    r.expire(key, LOCATION_TTL)


def get_guard_location(guard_id: int) -> dict | None:
    """Get guard's current location from Redis. Returns None if offline/expired."""
    r = get_redis()
    data = r.hgetall(f"bsecure:location:guard:{guard_id}")
    if not data:
        return None
    return {
        "lat": float(data["lat"]),
        "lon": float(data["lon"]),
        "heading": float(data["heading"]),
        "speed": float(data["speed"]),
        "updated_at": data["updated_at"],
        "booking_id": int(data["booking_id"]) if data.get("booking_id") else None,
    }


def delete_guard_location(guard_id: int):
    """Remove guard location from Redis (e.g., on explicit offline)."""
    r = get_redis()
    r.delete(f"bsecure:location:guard:{guard_id}")
