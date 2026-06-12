from django.db import models
from django.utils import timezone
from utils.models import TimeStampedModel


class OTPToken(TimeStampedModel):
    """
    Stores hashed OTP tokens for phone number verification.
    One active token per phone number at a time.
    """

    phone_number = models.CharField(max_length=20, db_index=True)
    otp_hash = models.CharField(max_length=64)  # SHA-256 hash of the OTP
    role = models.CharField(
        max_length=10,
        choices=[("USER", "User"), ("GUARD", "Guard"), ("ADMIN", "Admin")],
        default="USER",
    )
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    failed_attempts = models.PositiveSmallIntegerField(default=0)

    # Rate limiting metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = "auth_otp_token"
        indexes = [
            models.Index(fields=["phone_number", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_locked(self) -> bool:
        from django.conf import settings

        return self.failed_attempts >= getattr(settings, "OTP_MAX_ATTEMPTS", 3)

    def __str__(self):
        return f"OTP for {self.phone_number} [used={self.is_used}, expired={self.is_expired}]"
