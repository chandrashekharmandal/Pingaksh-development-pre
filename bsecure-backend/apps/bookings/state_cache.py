"""
Booking state cache for WebSocket consumers.

Key: bsecure:booking:{booking_id}:state (Hash, TTL=86400s)
Allows consumers to read booking state without a DB query on every location update.
"""

from apps.core.redis_client import get_redis


BOOKING_STATE_TTL = 86400  # 24 hours


def cache_booking_state(booking):
    """Cache booking state from a Booking model instance."""
    r = get_redis()
    key = f"bsecure:booking:{booking.id}:state"
    r.hset(
        key,
        mapping={
            "status": booking.status,
            "guard_id": str(booking.guard_id) if booking.guard_id else "",
            "user_id": str(booking.user_id),
            "started_at": booking.started_at.isoformat()
            if getattr(booking, "started_at", None)
            else "",
            "scheduled_at": booking.scheduled_at.isoformat()
            if getattr(booking, "scheduled_at", None)
            else "",
        },
    )
    r.expire(key, BOOKING_STATE_TTL)


def get_booking_state(booking_id: int) -> dict | None:
    """Get cached booking state. Returns None if not cached."""
    r = get_redis()
    data = r.hgetall(f"bsecure:booking:{booking_id}:state")
    return data if data else None


def invalidate_booking_state(booking_id: int):
    """Remove booking state from cache (on terminal state)."""
    get_redis().delete(f"bsecure:booking:{booking_id}:state")
