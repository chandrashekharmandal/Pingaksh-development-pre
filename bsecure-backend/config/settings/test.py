"""
Test settings — uses SQLite (no PostGIS) so tests run without a real database server.
PostGIS-specific fields are swapped to plain geometry via mock where needed.
"""

import environ
from pathlib import Path
from datetime import timedelta
from kombu import Queue, Exchange

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # NOTE: django.contrib.gis excluded in test — using plain DB backend
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
        "DIRS": [],
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

# SQLite for fast tests — no PostGIS needed
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# In-memory channel layer for tests
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media_test"

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

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "b-secure API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.apple.AppleIdAuth",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "test"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "test"
SOCIAL_AUTH_APPLE_ID_CLIENT = "test"
SOCIAL_AUTH_APPLE_ID_TEAM = "test"
SOCIAL_AUTH_APPLE_ID_KEY = "test"
SOCIAL_AUTH_APPLE_ID_SECRET = "test"

CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

# Celery — synchronous for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

CELERY_TASK_QUEUES = (
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
    Queue("scheduled", Exchange("scheduled"), routing_key="scheduled"),
)
CELERY_TASK_DEFAULT_QUEUE = "default"

# OTP settings
OTP_EXPIRY_SECONDS = 300
OTP_LENGTH = 6
OTP_MAX_ATTEMPTS = 3
OTP_RATE_LIMIT_COUNT = 5
OTP_RATE_LIMIT_WINDOW = 600

# Booking settings
BOOKING_BROADCAST_RADIUS_KM = 5
BOOKING_BROADCAST_MAX_RADIUS_KM = 20
BOOKING_BROADCAST_TIMEOUT_SECONDS = 600
BOOKING_PLATFORM_FEE_PERCENT = 15
BOOKING_TAX_PERCENT = 18

SOS_ESCALATION_TIMEOUT_SECONDS = 120

# Notification backends (console for tests)
SMS_BACKEND = "console"
PUSH_BACKEND = "console"

# External service keys (mocked in tests)
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = ""
TWILIO_ACCOUNT_SID = "test"
TWILIO_AUTH_TOKEN = "test"
TWILIO_PHONE_NUMBER = "+15005550006"
MSG91_AUTH_KEY = "test"
MSG91_TEMPLATE_ID = "test"
SENDGRID_API_KEY = "test"
DEFAULT_FROM_EMAIL = "noreply@bsecure.in"
RAZORPAY_KEY_ID = "test"
RAZORPAY_KEY_SECRET = "test"
RAZORPAY_WEBHOOK_SECRET = "test"
STRIPE_SECRET_KEY = "test"
STRIPE_WEBHOOK_SECRET = "test"
STRIPE_PUBLISHABLE_KEY = "test"
GOOGLE_MAPS_API_KEY = "test"
IDFY_API_KEY = "test"
IDFY_ACCOUNT_ID = "test"

# AWS (not used in tests)
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"
AWS_STORAGE_BUCKET_NAME = "test-bucket"
AWS_S3_REGION_NAME = "ap-south-1"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "root": {"handlers": ["null"]},
}
