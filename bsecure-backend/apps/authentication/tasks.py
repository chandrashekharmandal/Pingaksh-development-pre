"""Celery tasks for authentication app."""

from celery import shared_task
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(queue="scheduled", name="apps.authentication.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Nightly: clean up expired OTP tokens and JWT blacklist entries.
    Prevents these tables from growing unboundedly.
    """
    from django.utils import timezone
    from apps.authentication.models import OTPToken

    deleted_otps, _ = OTPToken.objects.filter(
        created_at__lt=timezone.now() - timedelta(hours=24)
    ).delete()

    deleted_jwts = 0
    try:
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

        deleted_jwts = BlacklistedToken.objects.filter(
            token__expires_at__lt=timezone.now()
        ).delete()[0]
    except Exception as e:
        logger.warning(f"Could not clean blacklisted JWTs: {e}")

    logger.info(f"Cleaned up {deleted_otps} OTPs, {deleted_jwts} blacklisted JWTs")
    return f"Cleaned up {deleted_otps} OTPs, {deleted_jwts} blacklisted JWTs"
