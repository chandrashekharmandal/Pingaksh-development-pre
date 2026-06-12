import redis
from django.conf import settings
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/health/
    Returns connectivity status for DB and Redis.
    """
    db_ok = False
    redis_ok = False

    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        pass

    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        redis_ok = True
    except Exception:
        pass

    overall = "ok" if db_ok and redis_ok else "degraded"

    return Response(
        {
            "status": overall,
            "db": "connected" if db_ok else "error",
            "redis": "connected" if redis_ok else "error",
            "version": "1.0.0",
        },
        status=200 if overall == "ok" else 503,
    )
