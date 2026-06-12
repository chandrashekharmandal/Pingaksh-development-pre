"""SOS Service — business logic for SOS alerts."""

import logging
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class SOSService:
    @staticmethod
    def trigger_sos(
        user,
        trigger_method: str,
        latitude: float,
        longitude: float,
        booking=None,
    ) -> "SOSAlert":
        """
        Core SOS trigger method.
        DB write and WS broadcast are synchronous (must be fast < 500ms).
        Everything else is async via Celery.
        """
        from .models import SOSAlert
        from .tasks import notify_emergency_contacts, schedule_sos_escalation
        from apps.notifications.tasks import notify_guard_of_user_sos

        # STEP 1: Write SOS record (synchronous — must never fail silently)
        sos = SOSAlert.objects.create(
            user=user,
            booking=booking,
            trigger_method=trigger_method,
            latitude=latitude,
            longitude=longitude,
            status="TRIGGERED",
        )

        logger.critical(
            f"SOS TRIGGERED: id={sos.id} user={user.id} "
            f"method={trigger_method} lat={latitude} lng={longitude} "
            f"booking={booking.id if booking else None}"
        )

        # STEP 2: Real-time broadcast to admin control room
        SOSService._broadcast_to_admins(sos)

        # STEP 3: Async — notify emergency contacts
        notify_emergency_contacts.apply_async(
            args=[str(sos.id)],
            queue="high_priority",
            countdown=0,
        )

        # STEP 4: Async — notify guard if session is active
        if booking and booking.status == "ACTIVE":
            notify_guard_of_user_sos.apply_async(
                args=[str(booking.id)],
                queue="high_priority",
                countdown=0,
            )

        # STEP 5: Schedule escalation if no admin responds within 5 minutes
        schedule_sos_escalation.apply_async(
            args=[str(sos.id)],
            countdown=300,
            queue="high_priority",
        )

        return sos

    @staticmethod
    def _broadcast_to_admins(sos: "SOSAlert"):
        """Broadcast new SOS to all connected admin WebSocket clients."""
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_sos_feed",
                {
                    "type": "sos_alert",
                    "payload": {
                        "event": "NEW_SOS",
                        "sos_id": str(sos.id),
                        "user_id": str(sos.user_id),
                        "user_name": sos.user.display_name,
                        "booking_id": str(sos.booking_id) if sos.booking_id else None,
                        "trigger_method": sos.trigger_method,
                        "latitude": float(sos.latitude),
                        "longitude": float(sos.longitude),
                        "triggered_at": sos.created_at.isoformat(),
                        "maps_link": f"https://maps.google.com/?q={sos.latitude},{sos.longitude}",
                    },
                },
            )
        except Exception as e:
            logger.warning(f"WS broadcast to admins failed: {e}")

    @staticmethod
    def acknowledge_sos(sos_id: str, admin_user) -> "SOSAlert":
        from .models import SOSAlert

        sos = SOSAlert.objects.get(id=sos_id)
        if sos.status == "TRIGGERED":
            sos.status = "ACKNOWLEDGED"
            sos.assigned_to = admin_user
            sos.acknowledged_at = timezone.now()
            sos.save(update_fields=["status", "assigned_to", "acknowledged_at"])
            SOSService._broadcast_status_update(sos)
        return sos

    @staticmethod
    def resolve_sos(
        sos_id: str, admin_user, notes: str, is_false_alarm: bool = False
    ) -> "SOSAlert":
        from .models import SOSAlert

        sos = SOSAlert.objects.get(id=sos_id)
        sos.status = "FALSE_ALARM" if is_false_alarm else "RESOLVED"
        sos.resolved_at = timezone.now()
        sos.resolution_notes = notes
        sos.save()
        SOSService._broadcast_status_update(sos)
        return sos

    @staticmethod
    def _broadcast_status_update(sos: "SOSAlert"):
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_sos_feed",
                {
                    "type": "sos_status_update",
                    "payload": {
                        "event": "SOS_STATUS_CHANGE",
                        "sos_id": str(sos.id),
                        "new_status": sos.status,
                        "timestamp": timezone.now().isoformat(),
                    },
                },
            )
        except Exception as e:
            logger.warning(f"WS SOS status broadcast failed: {e}")
