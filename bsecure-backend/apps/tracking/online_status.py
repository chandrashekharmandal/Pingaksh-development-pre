"""
Guard online status management via Redis.

Uses a dual-key pattern:
- Set: bsecure:online:guards — members are guard IDs (fast membership checks)
- String: bsecure:status:guard:{guard_id} — TTL=60s heartbeat key

Guard sends heartbeat every 30s. If 2 consecutive pings are missed (60s TTL expires),
the guard is automatically considered offline.
"""

from apps.core.redis_client import get_redis


HEARTBEAT_TTL = 60  # seconds — key expires if no heartbeat for 60s
HEARTBEAT_INTERVAL = 30  # client should ping every 30s


def go_online(guard_id: int):
    """Mark guard as online: add to SET and create heartbeat key."""
    r = get_redis()
    pipe = r.pipeline()
    pipe.sadd("bsecure:online:guards", str(guard_id))
    pipe.set(f"bsecure:status:guard:{guard_id}", "1", ex=HEARTBEAT_TTL)
    pipe.execute()


def go_offline(guard_id: int):
    """Mark guard as offline: remove from SET and delete heartbeat key."""
    r = get_redis()
    pipe = r.pipeline()
    pipe.srem("bsecure:online:guards", str(guard_id))
    pipe.delete(f"bsecure:status:guard:{guard_id}")
    pipe.execute()


def heartbeat(guard_id: int):
    """Called by guard app every 30s to reset the TTL."""
    r = get_redis()
    if r.sismember("bsecure:online:guards", str(guard_id)):
        r.set(f"bsecure:status:guard:{guard_id}", "1", ex=HEARTBEAT_TTL)
    else:
        go_online(guard_id)


def is_online(guard_id: int) -> bool:
    """Check if a guard is online (heartbeat key exists)."""
    r = get_redis()
    return bool(r.exists(f"bsecure:status:guard:{guard_id}"))


def get_online_guard_ids() -> set[int]:
    """Get all currently online guard IDs from the SET."""
    r = get_redis()
    return {int(gid) for gid in r.smembers("bsecure:online:guards")}


def sync_online_set():
    """
    Reconcile the online:guards SET with heartbeat keys.
    Remove guards whose heartbeat key has expired (stale SET entries).
    Called by Celery beat every 1 minute.
    """
    r = get_redis()
    online_ids = r.smembers("bsecure:online:guards")
    stale = []
    for gid in online_ids:
        if not r.exists(f"bsecure:status:guard:{gid}"):
            stale.append(gid)
    if stale:
        r.srem("bsecure:online:guards", *stale)
    return len(stale)
