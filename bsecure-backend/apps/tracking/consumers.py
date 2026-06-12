import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class TrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time guard location tracking.
    URL: /ws/tracking/{booking_id}/
    """

    async def connect(self):
        self.booking_id = self.scope["url_route"]["kwargs"]["booking_id"]
        self.session_group = f"session_{self.booking_id}"
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close(code=4001)
            return

        booking = await self._get_booking()
        if not booking:
            await self.close(code=4004)
            return

        if not await self._is_participant(booking):
            await self.close(code=4003)
            return

        self.booking = booking
        self.is_guard = await self._check_is_guard()

        await self.channel_layer.group_add(self.session_group, self.channel_name)

        if self.user.is_staff:
            await self.channel_layer.group_add("admin_live_map", self.channel_name)

        await self.accept()
        logger.info(
            f"WS tracking connected: user={self.user.id} booking={self.booking_id}"
        )

        await self.send(
            text_data=json.dumps(
                {
                    "type": "session_state",
                    "status": self.booking.status,
                    "booking_id": str(self.booking_id),
                }
            )
        )

    async def disconnect(self, close_code):
        if hasattr(self, "session_group"):
            await self.channel_layer.group_discard(
                self.session_group, self.channel_name
            )
        if hasattr(self, "user") and self.user.is_staff:
            await self.channel_layer.group_discard("admin_live_map", self.channel_name)
        logger.info(f"WS tracking disconnected code={close_code}")

    async def receive(self, text_data):
        if not self.is_guard:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "code": "NOT_PERMITTED",
                        "message": "Only the assigned guard can send location updates.",
                    }
                )
            )
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_type = data.get("type")
        if message_type == "location_update":
            await self._handle_location_update(data)
        elif message_type == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def _handle_location_update(self, data: dict):
        lat = data.get("lat")
        lng = data.get("lng")
        accuracy = data.get("accuracy")

        if not lat or not lng:
            return

        await self._save_location_snapshot(
            lat, lng, accuracy, data.get("speed"), data.get("bearing")
        )
        await self._update_guard_location(lat, lng)

        outbound = {
            "type": "guard_location",
            "lat": lat,
            "lng": lng,
            "accuracy": accuracy,
            "speed": data.get("speed"),
            "bearing": data.get("bearing"),
            "eta_seconds": None,
            "timestamp": timezone.now().isoformat(),
        }
        await self.channel_layer.group_send(
            self.session_group,
            {
                "type": "broadcast_message",
                "payload": outbound,
            },
        )

        await self.channel_layer.group_send(
            "admin_live_map",
            {
                "type": "broadcast_message",
                "payload": {
                    **outbound,
                    "booking_id": str(self.booking_id),
                },
            },
        )

    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    async def session_status_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "session_status_change",
                    "status": event["status"],
                    "timestamp": event.get("timestamp"),
                }
            )
        )

    @database_sync_to_async
    def _get_booking(self):
        from apps.bookings.models import Booking

        try:
            return Booking.objects.select_related("user", "guard__user").get(
                id=self.booking_id
            )
        except Booking.DoesNotExist:
            return None

    @database_sync_to_async
    def _is_participant(self, booking) -> bool:
        if self.user.is_staff:
            return True
        if booking.user_id == self.user.id:
            return True
        if (
            hasattr(self.user, "guard_profile")
            and booking.guard == self.user.guard_profile
        ):
            return True
        return False

    @database_sync_to_async
    def _check_is_guard(self) -> bool:
        return (
            hasattr(self.user, "guard_profile")
            and self.booking.guard == self.user.guard_profile
        )

    @database_sync_to_async
    def _save_location_snapshot(self, lat, lng, accuracy, speed, bearing):
        from apps.tracking.models import LocationSnapshot

        # Build location value: PostGIS Point in production, string in SQLite test env
        try:
            from django.contrib.gis.geos import Point

            location_value = Point(float(lng), float(lat), srid=4326)
        except Exception:
            location_value = f"{lat},{lng}"

        LocationSnapshot.objects.create(
            booking=self.booking,
            guard=self.booking.guard,
            location=location_value,
            accuracy_meters=accuracy or 0,
            speed_kmh=speed,
            bearing_degrees=bearing,
            timestamp=timezone.now(),
        )

    @database_sync_to_async
    def _update_guard_location(self, lat, lng):
        from apps.guards.models import GuardProfile

        GuardProfile.objects.filter(id=self.booking.guard_id).update(
            last_location_update=timezone.now(),
        )
