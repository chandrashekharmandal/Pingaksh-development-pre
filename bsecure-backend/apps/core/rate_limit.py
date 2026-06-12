"""
Redis-based rate limiting (fixed window counter).

Key: bsecure:ratelimit:{scope}:{user_id}:{window}
"""

import time
from functools import wraps

from rest_framework.response import Response

from apps.core.redis_client import get_redis


def rate_limit(max_requests: int, window_seconds: int, scope: str = "api"):
    """
    DRF APIView method decorator for Redis-based rate limiting.
    Uses a fixed-window counter pattern.

    Usage:
        class MyView(APIView):
            @rate_limit(max_requests=30, window_seconds=60, scope="nearby_guards")
            def get(self, request):
                ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            try:
                r = get_redis()
                user_id = (
                    request.user.id
                    if request.user.is_authenticated
                    else request.META.get("REMOTE_ADDR", "anon")
                )
                window = int(time.time() // window_seconds)
                key = f"bsecure:ratelimit:{scope}:{user_id}:{window}"

                count = r.incr(key)
                if count == 1:
                    r.expire(key, window_seconds + 5)  # small buffer for clock skew

                if count > max_requests:
                    return Response(
                        {
                            "error": {
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": f"Rate limit exceeded. Max {max_requests} requests per {window_seconds}s.",
                                "details": {"retry_after": window_seconds},
                            }
                        },
                        status=429,
                        headers={"Retry-After": str(window_seconds)},
                    )
            except Exception:
                # If Redis is down, allow the request (fail-open)
                pass

            return view_func(self, request, *args, **kwargs)

        return wrapper

    return decorator
