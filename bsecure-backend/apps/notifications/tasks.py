"""Celery tasks for notifications app."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.notifications.tasks.send_push_notification", queue="default")
def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    """
    Send FCM push notification to a user.
    Logs to console in test/dev environments.
    """
    from apps.users.models import UserProfile
    from apps.notifications.models import NotificationLog
    from django.conf import settings

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        logger.warning(f"Push notification: user {user_id} not found")
        return

    # Log notification to DB for in-app feed
    NotificationLog.objects.create(
        recipient=user,
        channel="PUSH",
        notification_type=(data or {}).get("action", "GENERAL"),
        title=title,
        body=body,
    )

    backend = getattr(settings, "PUSH_BACKEND", "console")
    if backend == "console":
        logger.info(f"[PUSH] → {user.phone_number}: {title} — {body}")
        return

    fcm_token = getattr(user, "fcm_token", None)
    if not fcm_token:
        logger.debug(f"Push notification skipped: user {user_id} has no FCM token")
        return

    # In production, send via FCM SDK
    try:
        import firebase_admin.messaging as fcm
        from firebase_admin import credentials, initialize_app

        message = fcm.Message(
            notification=fcm.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=fcm_token,
        )
        fcm.send(message)
    except Exception as e:
        logger.error(f"FCM send failed for user {user_id}: {e}")


@shared_task(name="apps.notifications.tasks.send_sms", queue="default")
def send_sms(phone_number: str, message: str):
    """Send SMS via configured provider (Twilio / MSG91)."""
    from django.conf import settings

    backend = getattr(settings, "SMS_BACKEND", "console")
    if backend == "console":
        logger.info(f"[SMS] → {phone_number}: {message}")
        return

    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
        )
    except Exception as e:
        logger.error(f"SMS send failed to {phone_number}: {e}")


@shared_task(name="apps.notifications.tasks.send_email", queue="low_priority")
def send_email(to_email: str, subject: str, body: str):
    """Send email via Django's email backend."""
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")


@shared_task(
    name="apps.notifications.tasks.notify_guard_of_user_sos", queue="high_priority"
)
def notify_guard_of_user_sos(booking_id: str):
    """Alert the assigned guard that the user triggered an SOS."""
    from apps.bookings.models import Booking

    try:
        booking = Booking.objects.select_related("guard__user").get(id=booking_id)
    except Booking.DoesNotExist:
        return

    guard_user = booking.guard.user
    send_push_notification.delay(
        str(guard_user.id),
        "⚠️ SOS ALERT",
        "Your client has triggered an emergency SOS. Please respond immediately.",
        {"action": "USER_SOS", "booking_id": booking_id},
    )
