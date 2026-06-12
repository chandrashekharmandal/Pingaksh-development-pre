import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.authentication.models import OTPToken
from utils.helpers import generate_secure_otp, hash_otp, verify_otp

logger = logging.getLogger(__name__)

User = get_user_model()


class OTPService:
    OTP_EXPIRY_SECONDS = getattr(settings, "OTP_EXPIRY_SECONDS", 300)
    OTP_LENGTH = getattr(settings, "OTP_LENGTH", 6)
    MAX_ATTEMPTS = getattr(settings, "OTP_MAX_ATTEMPTS", 3)

    @classmethod
    def send_otp(
        cls, phone_number: str, role: str = "USER", ip_address: str = None
    ) -> OTPToken:
        """
        Generate a new OTP, store the hash, and dispatch via SMS.
        Invalidates any previous unused OTPs for this phone.
        """
        # Mark previous tokens as used
        OTPToken.objects.filter(
            phone_number=phone_number,
            is_used=False,
        ).update(is_used=True)

        otp = generate_secure_otp(cls.OTP_LENGTH)
        token = OTPToken.objects.create(
            phone_number=phone_number,
            otp_hash=hash_otp(otp),
            role=role,
            expires_at=timezone.now() + timedelta(seconds=cls.OTP_EXPIRY_SECONDS),
            ip_address=ip_address,
        )

        cls._dispatch_otp(phone_number, otp)
        logger.info(f"OTP sent to {phone_number}")
        return token

    @classmethod
    def verify_otp(cls, phone_number: str, otp_code: str, role: str = "USER") -> User:
        """
        Verify OTP and return (or create) the associated user.

        Raises:
            OTPExpiredError, OTPInvalidError, OTPLockedError
        """
        from utils.exceptions import OTPExpiredError, OTPInvalidError, OTPLockedError

        try:
            token = OTPToken.objects.filter(
                phone_number=phone_number,
                is_used=False,
                role=role,
            ).latest("created_at")
        except OTPToken.DoesNotExist:
            raise OTPInvalidError("No OTP found for this phone number.")

        if token.is_locked:
            raise OTPLockedError()

        if token.is_expired:
            raise OTPExpiredError()

        if not verify_otp(otp_code, token.otp_hash):
            token.failed_attempts += 1
            token.save(update_fields=["failed_attempts"])
            if token.is_locked:
                raise OTPLockedError()
            raise OTPInvalidError()

        # Mark as used
        token.is_used = True
        token.save(update_fields=["is_used"])

        # Get or create user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"role": role, "is_active": True},
        )

        if created:
            logger.info(f"New user created: {phone_number} [{role}]")
            if role == "GUARD":
                cls._create_guard_profile(user)

        return user, created

    @staticmethod
    def _create_guard_profile(user):
        """Auto-create a GuardProfile when a guard registers."""
        from apps.guards.models import GuardProfile

        GuardProfile.objects.get_or_create(user=user)

    @staticmethod
    def _dispatch_otp(phone_number: str, otp: str):
        """Send OTP via configured SMS backend."""
        backend = getattr(settings, "SMS_BACKEND", "console")

        if backend == "console":
            logger.debug(f"[DEV] OTP for {phone_number}: {otp}")
            return

        if backend == "twilio":
            from apps.notifications.services.sms import SMSService

            SMSService.send_otp_sms(phone_number, otp)
        elif backend == "msg91":
            from apps.notifications.services.sms import SMSService

            SMSService.send_otp_via_msg91(phone_number, otp)
