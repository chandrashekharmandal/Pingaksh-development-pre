"""
FCM push notification token store via Redis.

Key: bsecure:fcm:{entity_type}:{entity_id} (Hash, no TTL)
Fields: token, platform, updated_at
"""

from django.utils import timezone

from apps.core.redis_client import get_redis


def store_fcm_token(entity_type: str, entity_id: int, token: str, platform: str):
    """
    Store FCM token for a user or guard.

    Args:
        entity_type: 'user' or 'guard'
        entity_id: user ID or guard ID
        token: FCM registration token
        platform: 'android' or 'ios'
    """
    r = get_redis()
    key = f"bsecure:fcm:{entity_type}:{entity_id}"
    r.hset(
        key,
        mapping={
            "token": token,
            "platform": platform,
            "updated_at": timezone.now().isoformat(),
        },
    )


def get_fcm_token(entity_type: str, entity_id: int) -> str | None:
    """Get the FCM token for a user or guard. Returns None if not stored."""
    r = get_redis()
    data = r.hgetall(f"bsecure:fcm:{entity_type}:{entity_id}")
    return data.get("token") if data else None


def get_fcm_data(entity_type: str, entity_id: int) -> dict | None:
    """Get full FCM data (token, platform, updated_at)."""
    r = get_redis()
    data = r.hgetall(f"bsecure:fcm:{entity_type}:{entity_id}")
    return data if data else None


def delete_fcm_token(entity_type: str, entity_id: int):
    """Remove FCM token (on logout or token refresh)."""
    get_redis().delete(f"bsecure:fcm:{entity_type}:{entity_id}")
