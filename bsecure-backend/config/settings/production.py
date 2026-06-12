from .base import *  # noqa: F401, F403
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405

# ─── Security Headers ─────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# ─── Database (PostgreSQL + PostGIS) ─────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_NAME"),  # noqa: F405
        "USER": env("DB_USER"),  # noqa: F405
        "PASSWORD": env("DB_PASSWORD"),  # noqa: F405
        "HOST": env("DB_HOST"),  # noqa: F405
        "PORT": env("DB_PORT", default="5432"),  # noqa: F405
        "CONN_MAX_AGE": 60,
        "OPTIONS": {"sslmode": "require"},
    }
}

# ─── Redis Cache (ElastiCache, TLS) ──────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,  # noqa: F405
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
            },
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "IGNORE_EXCEPTIONS": False,
        },
        "KEY_PREFIX": "bsecure",
        "TIMEOUT": 300,
    }
}

# ─── Redis Channel Layer (DB 2) ──────────────────────────────────────────────
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_CHANNELS_URL],  # noqa: F405
            "capacity": 1500,
            "expiry": 10,
            "group_expiry": 86400,
            "channel_capacity": {
                "http.request": 200,
                "websocket.send*": 20,
            },
        },
    },
}

# ─── S3 Storage ──────────────────────────────────────────────────────────────
STORAGES = {
    "default": {
        "BACKEND": "config.storages.PrivateMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "config.storages.PublicMediaStorage",
    },
}
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = env("AWS_S3_BUCKET_NAME")  # noqa: F405
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="ap-south-1")  # noqa: F405
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "private"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_CUSTOM_DOMAIN = None  # Use default S3 domain for private objects
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 900  # 15 minutes for pre-signed URLs

# ─── Sentry ───────────────────────────────────────────────────────────────────
sentry_sdk.init(
    dsn=env("SENTRY_DSN"),  # noqa: F405
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=0.2,
    send_default_pii=False,
)

# ─── Logging (JSON) ─────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "celery": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

SMS_BACKEND = "twilio"
PUSH_BACKEND = "fcm"
