"""
Guard leaderboard operations via Redis Sorted Sets.

Keys:
- bsecure:leaderboard:guards:rating — guards ranked by average rating
- bsecure:leaderboard:guards:bookings:{YYYY-MM} — guards ranked by monthly bookings
"""

from apps.core.redis_client import get_redis


RATING_LEADERBOARD_KEY = "bsecure:leaderboard:guards:rating"


# ─── Rating Leaderboard ──────────────────────────────────────────────────────


def update_guard_rating_score(guard_id: int, average_rating: float):
    """Update guard's score in the rating leaderboard."""
    r = get_redis()
    r.zadd(RATING_LEADERBOARD_KEY, {str(guard_id): average_rating})


def get_top_guards_by_rating(n: int = 10) -> list[tuple[str, float]]:
    """Returns [(guard_id_str, score), ...] descending by rating."""
    r = get_redis()
    return r.zrevrange(RATING_LEADERBOARD_KEY, 0, n - 1, withscores=True)


def get_guard_rating_rank(guard_id: int) -> int | None:
    """Returns 0-based rank (0 = highest rated). None if not in leaderboard."""
    r = get_redis()
    return r.zrevrank(RATING_LEADERBOARD_KEY, str(guard_id))


def remove_guard_from_leaderboard(guard_id: int):
    """Remove guard from the rating leaderboard."""
    r = get_redis()
    r.zrem(RATING_LEADERBOARD_KEY, str(guard_id))


# ─── Monthly Bookings Leaderboard ────────────────────────────────────────────


def _get_monthly_bookings_key(year: int, month: int) -> str:
    return f"bsecure:leaderboard:guards:bookings:{year:04d}-{month:02d}"


def increment_guard_booking_count(guard_id: int, year: int, month: int):
    """Increment guard's completed booking count for the given month."""
    r = get_redis()
    key = _get_monthly_bookings_key(year, month)
    r.zincrby(key, 1, str(guard_id))
    # Expire monthly leaderboard 90 days after month end
    r.expire(key, 90 * 86400)


def get_top_guards_by_bookings(
    year: int, month: int, n: int = 10
) -> list[tuple[str, float]]:
    """Returns [(guard_id_str, count), ...] descending by booking count."""
    r = get_redis()
    key = _get_monthly_bookings_key(year, month)
    return r.zrevrange(key, 0, n - 1, withscores=True)
