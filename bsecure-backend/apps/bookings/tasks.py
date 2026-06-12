"""Celery tasks for the bookings app."""

from celery import shared_task
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=1,
    queue="high_priority",
    name="apps.bookings.tasks.broadcast_booking_request",
)
def broadcast_booking_request(self, booking_id: str, radius_km: int = 5):
    """
    Broadcast a booking request to all nearby available guards.
    Falls back to guard-type-only search if PostGIS unavailable.
    """
    from apps.bookings.models import Booking, BookingBroadcast
    from apps.guards.models import GuardProfile
    from django.utils import timezone

    try:
        booking = Booking.objects.select_related("user").get(id=booking_id)
    except Booking.DoesNotExist:
        return

    if booking.status not in ("REQUESTED", "BROADCAST"):
        return

    if booking.status == "REQUESTED":
        booking.start_broadcast()
        booking.save()

    already_sent = BookingBroadcast.objects.filter(booking=booking).values_list(
        "guard_id", flat=True
    )

    # Try PostGIS distance filter; fall back to basic filter if unavailable
    try:
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D

        user_location = Point(
            float(booking.service_longitude),
            float(booking.service_latitude),
            srid=4326,
        )
        nearby_guards = (
            GuardProfile.objects.filter(
                is_online=True,
                verification_status="ACTIVE",
                guard_type=booking.guard_type_requested,
                current_location__distance_lte=(user_location, D(km=radius_km)),
            )
            .exclude(id__in=already_sent)
            .order_by("?")[:15]
        )
    except Exception:
        nearby_guards = (
            GuardProfile.objects.filter(
                is_online=True,
                verification_status="ACTIVE",
                guard_type=booking.guard_type_requested,
            )
            .exclude(id__in=already_sent)
            .order_by("?")[:15]
        )

    if not nearby_guards.exists():
        if radius_km < 10:
            logger.info(
                f"Booking {booking_id}: no guards in {radius_km}km, "
                f"expanding to {radius_km + 5}km"
            )
            broadcast_booking_request.apply_async(
                args=[booking_id, radius_km + 5],
                countdown=90,
                queue="high_priority",
            )
        else:
            expire_booking.apply_async(
                args=[booking_id],
                countdown=30,
                queue="high_priority",
            )
        return

    for guard in nearby_guards:
        BookingBroadcast.objects.get_or_create(
            booking=booking,
            guard=guard,
            defaults={"broadcast_radius_km": radius_km},
        )
        # Send push notification if guard has FCM token
        if getattr(guard.user, "fcm_token", None):
            from apps.notifications.tasks import send_push_notification

            send_push_notification.apply_async(
                args=[
                    str(guard.user.id),
                    "New Booking Request!",
                    f"{booking.service_type} — {booking.guard_type_requested} — accept in 30 sec",
                ],
                kwargs={
                    "data": {
                        "booking_id": str(booking_id),
                        "action": "NEW_BOOKING_REQUEST",
                    }
                },
                queue="high_priority",
            )

    # Schedule expiry if no guard accepts within 5 minutes
    expire_unaccepted_booking.apply_async(
        args=[booking_id],
        countdown=300,
        queue="high_priority",
    )

    return f"Broadcast to {nearby_guards.count()} guards within {radius_km}km"


@shared_task(queue="high_priority", name="apps.bookings.tasks.expire_unaccepted")
def expire_unaccepted_booking(booking_id: str):
    """Called 5 min after broadcast if booking still not accepted."""
    from apps.bookings.models import Booking

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return

    if booking.status == "BROADCAST":
        booking.expire()
        booking.save()
        logger.info(f"Booking {booking_id} expired — no guard accepted in time")


@shared_task(queue="high_priority", name="apps.bookings.tasks.expire_booking")
def expire_booking(booking_id: str):
    """Expire a booking that could not be matched with any guard."""
    from apps.bookings.models import Booking

    try:
        booking = Booking.objects.get(id=booking_id, status="BROADCAST")
        booking.expire()
        booking.save()
        logger.info(f"Booking {booking_id} expired — no guards found in max radius")
    except Booking.DoesNotExist:
        pass


@shared_task(queue="default", name="apps.bookings.tasks.expire_stale_broadcasts")
def expire_stale_broadcasts():
    """Expire BROADCAST bookings that have exceeded the timeout window."""
    from apps.bookings.models import Booking
    from django.utils import timezone
    from django.conf import settings

    timeout_seconds = getattr(settings, "BOOKING_BROADCAST_TIMEOUT_SECONDS", 600)
    cutoff = timezone.now() - timedelta(seconds=timeout_seconds)

    stale = Booking.objects.filter(status="BROADCAST", updated_at__lt=cutoff)
    count = 0
    for booking in stale:
        try:
            booking.expire()
            booking.save()
            count += 1
        except Exception as e:
            logger.warning(f"Could not expire booking {booking.id}: {e}")

    return f"Expired {count} stale broadcasts"


@shared_task(queue="default", name="apps.bookings.tasks.send_checkin_reminders")
def send_checkin_reminders():
    """Remind guards in ACTIVE long sessions to check in if due soon."""
    from apps.bookings.models import Booking, GuardCheckIn
    from django.utils import timezone
    from django.db.models import Max

    CHECKIN_INTERVAL_HOURS = 2
    WARNING_BEFORE_MINUTES = 15

    active = Booking.objects.filter(
        status="ACTIVE",
        service_type__in=["DAILY", "WEEKLY", "MONTHLY"],
    ).select_related("guard__user")

    now = timezone.now()
    count = 0

    for booking in active:
        last_checkin = GuardCheckIn.objects.filter(booking=booking).aggregate(
            last=Max("created_at")
        )["last"]

        reference = last_checkin or booking.session_started_at
        if not reference:
            continue

        minutes_since = (now - reference).total_seconds() / 60
        due_in_minutes = CHECKIN_INTERVAL_HOURS * 60 - minutes_since

        if 0 < due_in_minutes <= WARNING_BEFORE_MINUTES:
            from apps.notifications.tasks import send_push_notification

            send_push_notification.delay(
                str(booking.guard.user.id),
                "Check-in Reminder",
                f"Your session check-in is due in {int(due_in_minutes)} minutes.",
            )
            count += 1

    return f"Sent {count} check-in reminders"
