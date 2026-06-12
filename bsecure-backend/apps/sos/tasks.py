"""Celery tasks for the sos app."""

from celery import shared_task
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

CHECKIN_INTERVAL_HOURS = 2
CHECKIN_ESCALATION_MINUTES = 30


@shared_task(name="apps.sos.tasks.notify_emergency_contacts", queue="high_priority")
def notify_emergency_contacts(sos_alert_id: str):
    """
    Notify all emergency contacts for an SOS alert via SMS.
    """
    from apps.sos.models import SOSAlert, EmergencyContactAlert
    from apps.notifications.tasks import send_sms

    try:
        sos = SOSAlert.objects.select_related("user").get(id=sos_alert_id)
    except SOSAlert.DoesNotExist:
        return

    contacts = sos.user.emergency_contacts.all()
    maps_link = f"https://maps.google.com/?q={sos.latitude},{sos.longitude}"

    for contact in contacts:
        message = (
            f"EMERGENCY ALERT: {sos.user.display_name} has triggered an SOS. "
            f"Location: {maps_link}. Please check on them immediately."
        )
        send_sms.delay(contact.phone_number, message)

        EmergencyContactAlert.objects.update_or_create(
            sos_alert=sos,
            contact_phone=contact.phone_number,
            defaults={
                "contact_name": contact.name,
                "sms_sent": True,
            },
        )

    return f"Notified {contacts.count()} emergency contacts for SOS {sos_alert_id}"


@shared_task(name="apps.sos.tasks.schedule_sos_escalation", queue="high_priority")
def schedule_sos_escalation(sos_id: str):
    """
    Called 5 minutes after SOS is triggered.
    If still not acknowledged → send escalation SMS to supervisors.
    """
    from apps.sos.models import SOSAlert
    from django.conf import settings
    from apps.notifications.tasks import send_sms

    try:
        sos = SOSAlert.objects.select_related("user").get(id=sos_id)
    except SOSAlert.DoesNotExist:
        return

    if sos.status == "TRIGGERED":
        logger.critical(
            f"SOS ESCALATION: {sos_id} not acknowledged after 5 minutes! "
            f"User: {sos.user_id}"
        )

        supervisor_phones = getattr(settings, "SOS_SUPERVISOR_PHONES", [])
        for phone in supervisor_phones:
            send_sms.delay(
                phone,
                (
                    f"URGENT: SOS alert {str(sos_id)[:8]} has not been acknowledged "
                    f"for 5 minutes. User: {sos.user.display_name}. "
                    f"Location: https://maps.google.com/?q={sos.latitude},{sos.longitude}"
                ),
            )

        # Schedule second escalation in 10 more minutes
        schedule_second_escalation.apply_async(
            args=[sos_id],
            countdown=600,
            queue="high_priority",
        )


@shared_task(name="apps.sos.tasks.schedule_second_escalation", queue="high_priority")
def schedule_second_escalation(sos_id: str):
    """15 minutes after SOS — alert on-call engineer via email."""
    from apps.sos.models import SOSAlert
    from django.conf import settings
    from apps.notifications.tasks import send_email

    try:
        sos = SOSAlert.objects.get(id=sos_id)
    except SOSAlert.DoesNotExist:
        return

    if sos.status in ("TRIGGERED", "ACKNOWLEDGED"):
        logger.critical(f"SOS CRITICAL: {sos_id} unresolved at 15 min mark!")
        oncall_email = getattr(settings, "ONCALL_ENGINEER_EMAIL", None)
        if oncall_email:
            send_email.delay(
                oncall_email,
                f"CRITICAL: Unresolved SOS Alert {str(sos_id)[:8]}",
                f"SOS {sos_id} is unresolved after 15 minutes. Immediate action required.",
            )


@shared_task(
    name="apps.sos.tasks.escalate_sos_if_unacknowledged", queue="high_priority"
)
def escalate_sos_if_unacknowledged(sos_alert_id: str):
    """Legacy alias — delegates to schedule_sos_escalation."""
    return schedule_sos_escalation(sos_alert_id)


@shared_task(queue="default", name="apps.sos.tasks.monitor_session_checkins")
def monitor_session_checkins():
    """
    Runs every 15 minutes (Celery beat).
    Checks all active long sessions for missed check-ins.
    """
    from apps.bookings.models import Booking, GuardCheckIn
    from django.db.models import Max
    from django.utils import timezone

    active_sessions = Booking.objects.filter(
        status="ACTIVE",
        service_type__in=["DAILY", "WEEKLY", "MONTHLY"],
    ).select_related("user", "guard__user")

    now = timezone.now()

    for booking in active_sessions:
        last_checkin = GuardCheckIn.objects.filter(booking=booking).aggregate(
            last=Max("created_at")
        )["last"]

        reference_time = last_checkin or booking.session_started_at
        if not reference_time:
            continue

        minutes_since = (now - reference_time).total_seconds() / 60
        checkin_due_at = CHECKIN_INTERVAL_HOURS * 60

        if minutes_since >= checkin_due_at + CHECKIN_ESCALATION_MINUTES:
            _escalate_missed_checkin(booking)
        elif minutes_since >= checkin_due_at:
            _alert_missed_checkin(booking)


def _alert_missed_checkin(booking):
    from apps.notifications.tasks import send_push_notification
    from apps.notifications.models import NotificationLog
    from django.utils import timezone

    already_notified = NotificationLog.objects.filter(
        recipient=booking.user,
        notification_type="CHECKIN_MISSED",
        created_at__gte=timezone.now() - timedelta(hours=CHECKIN_INTERVAL_HOURS),
    ).exists()

    if not already_notified:
        send_push_notification.delay(
            str(booking.user.id),
            "Guard Check-in Missed",
            "Your guard has not checked in. Please verify they are safe.",
            {"action": "CHECKIN_MISSED", "booking_id": str(booking.id)},
        )


def _escalate_missed_checkin(booking):
    from apps.sos.services import SOSService

    logger.warning(
        f"Auto-escalating SOS for booking {booking.id}: "
        f"guard {booking.guard_id} missed check-in significantly"
    )

    SOSService.trigger_sos(
        user=booking.user,
        trigger_method="AUTO_CHECKIN",
        latitude=float(booking.service_latitude),
        longitude=float(booking.service_longitude),
        booking=booking,
    )


@shared_task(name="apps.sos.tasks.dead_mans_switch_check", queue="default")
def check_guard_offline_sessions():
    """
    Runs every 5 minutes (Celery beat).
    Detects guards who stopped sending location updates during active sessions.
    """
    from apps.bookings.models import Booking
    from apps.guards.models import GuardProfile
    from django.utils import timezone

    OFFLINE_THRESHOLD_MINUTES = 10
    threshold_time = timezone.now() - timedelta(minutes=OFFLINE_THRESHOLD_MINUTES)

    at_risk_bookings = Booking.objects.filter(
        status="ACTIVE",
        guard__last_location_update__lt=threshold_time,
        guard__is_online=True,
    ).select_related("user", "guard__user")

    for booking in at_risk_bookings:
        logger.error(
            f"Dead Man Switch: guard {booking.guard_id} offline during "
            f"active session {booking.id}"
        )

        GuardProfile.objects.filter(id=booking.guard_id).update(is_online=False)

        from apps.sos.services import SOSService

        SOSService.trigger_sos(
            user=booking.user,
            trigger_method="GUARD_OFFLINE",
            latitude=float(booking.service_latitude),
            longitude=float(booking.service_longitude),
            booking=booking,
        )
