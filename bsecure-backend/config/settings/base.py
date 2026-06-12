import environ
from pathlib import Path
from datetime import timedelta
from kombu import Queue, Exchange

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")

INSTALLED_APPS = [
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
    "storages",
    "social_django",
    "drf_spectacular",
    # b-secure apps
    "apps.authentication",
    "apps.users",
    "apps.guards",
    "apps.bookings",
    "apps.tracking",
    "apps.payments",
    "apps.notifications",
    "apps.sos",
    "apps.reviews",
    "apps.admin_panel",
    "apps.analytics",
    "apps.core",
]

AUTH_USER_MODEL = "users.UserProfile"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (overridden to S3 in production)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─── Django REST Framework ───────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "utils.exceptions.custom_exception_handler",
}

# ─── JWT ─────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=30)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ─── DRF Spectacular (OpenAPI) ────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "b-secure API",
    "DESCRIPTION": "b-secure Security Guard Booking Platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ─── Social Auth ─────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.apple.AppleIdAuth",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_OAUTH2_CLIENT_ID", default="")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("GOOGLE_OAUTH2_CLIENT_SECRET", default="")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["profile", "email"]

SOCIAL_AUTH_APPLE_ID_CLIENT = env("APPLE_CLIENT_ID", default="")
SOCIAL_AUTH_APPLE_ID_TEAM = env("APPLE_TEAM_ID", default="")
SOCIAL_AUTH_APPLE_ID_KEY = env("APPLE_KEY_ID", default="")
SOCIAL_AUTH_APPLE_ID_SECRET = env("APPLE_PRIVATE_KEY", default="")

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000", "http://localhost:19006"]
)

# ─── Firebase / FCM ──────────────────────────────────────────────────────────
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = env("FIREBASE_SERVICE_ACCOUNT_KEY_PATH", default="")

# ─── Twilio ───────────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_PHONE_NUMBER = env("TWILIO_PHONE_NUMBER", default="")

# ─── MSG91 (alternative SMS) ──────────────────────────────────────────────────
MSG91_AUTH_KEY = env("MSG91_AUTH_KEY", default="")
MSG91_TEMPLATE_ID = env("MSG91_TEMPLATE_ID", default="")

# ─── SendGrid ─────────────────────────────────────────────────────────────────
SENDGRID_API_KEY = env("SENDGRID_API_KEY", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@bsecure.in")

# ─── Razorpay ────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID = env("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = env("RAZORPAY_KEY_SECRET", default="")
RAZORPAY_WEBHOOK_SECRET = env("RAZORPAY_WEBHOOK_SECRET", default="")

# ─── Stripe ───────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")

# ─── Google Maps ─────────────────────────────────────────────────────────────
GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY", default="")

# ─── IDfy (Background Verification) ─────────────────────────────────────────
IDFY_API_KEY = env("IDFY_API_KEY", default="")
IDFY_ACCOUNT_ID = env("IDFY_ACCOUNT_ID", default="")

# ─── Redis URLs ──────────────────────────────────────────────────────────────
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
REDIS_CELERY_URL = env("REDIS_CELERY_URL", default="redis://localhost:6379/1")
REDIS_CHANNELS_URL = env("REDIS_CHANNELS_URL", default="redis://localhost:6379/2")

# ─── Django Cache (Redis DB 0) ───────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": "bsecure",
        "TIMEOUT": 300,
    }
}

# Session engine backed by Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ─── Celery ──────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = REDIS_CELERY_URL
CELERY_RESULT_BACKEND = REDIS_CELERY_URL
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Kolkata"
CELERY_ENABLE_UTC = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 300
CELERY_TASK_TIME_LIMIT = 360
CELERY_TASK_QUEUES = (
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
    Queue("scheduled", Exchange("scheduled"), routing_key="scheduled"),
)
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_MAX_RETRIES = 3

# ─── Celery Beat Schedule ────────────────────────────────────────────────────
from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    # Expire broadcasts that have no guard after 10 minutes
    "expire-stale-broadcasts": {
        "task": "apps.bookings.tasks.expire_stale_broadcasts",
        "schedule": 60.0,  # every 60 seconds
        "options": {"queue": "high_priority"},
    },
    # Guard check-in reminder every 30 minutes during active sessions
    "guard-checkin-reminder": {
        "task": "apps.bookings.tasks.send_checkin_reminders",
        "schedule": 1800.0,
        "options": {"queue": "default"},
    },
    # Nightly analytics aggregation at 00:05 IST
    "aggregate-daily-stats": {
        "task": "apps.analytics.tasks.aggregate_daily_stats",
        "schedule": crontab(hour=0, minute=5),
        "options": {"queue": "low_priority"},
    },
    # Process pending payouts daily at 10:00 IST
    "process-guard-payouts": {
        "task": "apps.payments.tasks.process_pending_payouts",
        "schedule": crontab(hour=10, minute=0),
        "options": {"queue": "default"},
    },
    # Check for document expiry every day at 09:00 IST
    "check-document-expiry": {
        "task": "apps.guards.tasks.check_document_expiry",
        "schedule": crontab(hour=9, minute=0),
        "options": {"queue": "low_priority"},
    },
    # Dead man's switch: check offline guards in active sessions every 2 minutes
    "dead-mans-switch": {
        "task": "apps.sos.tasks.dead_mans_switch_check",
        "schedule": 120.0,
        "options": {"queue": "high_priority"},
    },
    # Sync guard online status SET with heartbeat keys every 60 seconds
    "sync-guard-online-status": {
        "task": "apps.tracking.tasks.sync_guard_online_status",
        "schedule": 60.0,
        "options": {"queue": "default"},
    },
    # Push live dashboard stats to admin WebSocket every 30 seconds
    "push-live-dashboard-stats": {
        "task": "apps.admin_panel.tasks.push_live_dashboard_stats",
        "schedule": 30.0,
        "options": {"queue": "low_priority"},
    },
    # Cleanup old location snapshots (older than 30 days) daily at 02:00
    "cleanup-old-location-snapshots": {
        "task": "apps.analytics.tasks.cleanup_old_location_snapshots",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "low_priority"},
    },
    # Process weekly guard payouts every Monday at 10:00
    "process-weekly-payouts": {
        "task": "apps.payments.tasks.process_weekly_payouts",
        "schedule": crontab(hour=10, minute=0, day_of_week=1),
        "options": {"queue": "default"},
    },
    # Cleanup expired auth tokens daily at 03:00
    "cleanup-expired-tokens": {
        "task": "apps.authentication.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "low_priority"},
    },
}

# ─── OTP Settings ────────────────────────────────────────────────────────────
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6
OTP_MAX_ATTEMPTS = 3
OTP_RATE_LIMIT_COUNT = 5  # max OTPs per phone per window
OTP_RATE_LIMIT_WINDOW = 600  # 10 minutes

# ─── Booking Settings ────────────────────────────────────────────────────────
BOOKING_BROADCAST_RADIUS_KM = 5  # Initial search radius
BOOKING_BROADCAST_MAX_RADIUS_KM = 20  # Expand to this if no guards in initial radius
BOOKING_BROADCAST_TIMEOUT_SECONDS = 600  # 10 min — expire if no acceptance
BOOKING_PLATFORM_FEE_PERCENT = 15  # Platform takes 15%
BOOKING_TAX_PERCENT = 18  # GST 18%

# ─── SOS Settings ────────────────────────────────────────────────────────────
SOS_ESCALATION_TIMEOUT_SECONDS = 120  # 2 min — escalate if unacknowledged
