from django.db import models
from utils.models import TimeStampedModel


class NotificationLog(TimeStampedModel):
    """Records every notification sent through the platform."""

    CHANNEL_CHOICES = [
        ("PUSH", "Push Notification (FCM)"),
        ("SMS", "SMS"),
        ("EMAIL", "Email"),
        ("IN_APP", "In-App Notification"),
        ("WHATSAPP", "WhatsApp (future)"),
    ]

    STATUS_CHOICES = [
        ("QUEUED", "Queued in Celery"),
        ("SENT", "Sent to Provider"),
        ("DELIVERED", "Delivered to Device"),
        ("FAILED", "Failed to Send"),
        ("BOUNCED", "Bounced / Invalid"),
    ]

    recipient = models.ForeignKey(
        "users.UserProfile", on_delete=models.CASCADE, related_name="notifications"
    )
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    notification_type = models.CharField(max_length=50)  # e.g. 'GUARD_ASSIGNED'
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    data = models.JSONField(default=dict)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="QUEUED")
    provider_message_id = models.CharField(max_length=255, blank=True)
    failure_reason = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications_log"
        indexes = [
            models.Index(fields=["recipient", "is_read", "created_at"]),
            models.Index(fields=["notification_type", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notification_type} → {self.recipient} [{self.status}]"


class NotificationPreference(TimeStampedModel):
    """Per-user notification preferences per channel."""

    user = models.OneToOneField(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    marketing_push = models.BooleanField(default=False)
    marketing_email = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications_preference"

    def __str__(self):
        return f"NotifPrefs for {self.user}"
