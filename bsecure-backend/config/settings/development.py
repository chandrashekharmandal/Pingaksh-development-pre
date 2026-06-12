from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# ─── Database (PostGIS via Docker) ────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_NAME", default="bsecure"),  # noqa: F405
        "USER": env("DB_USER", default="bsecure"),  # noqa: F405
        "PASSWORD": env("DB_PASSWORD", default="dev_password"),  # noqa: F405
        "HOST": env("DB_HOST", default="localhost"),  # noqa: F405
        "PORT": env("DB_PORT", default="5432"),  # noqa: F405
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
        },
    }
}

# ─── S3 via MinIO (local) ────────────────────────────────────────────────────
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://localhost:9000")  # noqa: F405
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="bsecure_dev")  # noqa: F405
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="dev_password_123")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="bsecure-dev")  # noqa: F405
AWS_S3_REGION_NAME = "us-east-1"
AWS_DEFAULT_ACL = "private"
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True

# Local media fallback (if not using MinIO)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# ─── Debug Toolbar ────────────────────────────────────────────────────────────
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─── Logging ─────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# In dev, skip real SMS — just print to console
SMS_BACKEND = "console"
PUSH_BACKEND = "console"
