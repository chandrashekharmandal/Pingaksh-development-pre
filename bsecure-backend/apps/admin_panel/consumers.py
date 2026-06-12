import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """
    Admin live dashboard WebSocket.
    URL: /ws/admin/dashboard/

    Receives:
    - Live KPI updates (every 30 seconds, pushed by Celery beat)
    - New booking notifications
    - Guard online/offline events
    """

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous or not user.is_staff:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add("admin_dashboard", self.channel_name)
        await self.accept()
        logger.info(f"WS admin dashboard connected: admin={user.id}")

        # Send initial stats on connect
        stats = await self._get_live_stats()
        await self.send(text_data=json.dumps({"type": "initial_stats", "data": stats}))

    async def disconnect(self, close_code):
        if hasattr(self, "channel_layer"):
            await self.channel_layer.group_discard("admin_dashboard", self.channel_name)
        logger.info(f"WS admin dashboard disconnected code={close_code}")

    async def receive(self, text_data):
        # Admin dashboard is read-only; no inbound messages handled
        pass

    async def dashboard_update(self, event):
        """Called when Celery beat pushes live stats."""
        await self.send(text_data=json.dumps(event["payload"]))

    @staticmethod
    def broadcast_stats_update(stats: dict):
        """Called by Celery beat task every 30 seconds."""
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "admin_dashboard",
            {
                "type": "dashboard_update",
                "payload": {"event": "STATS_UPDATE", "data": stats},
            },
        )

    @database_sync_to_async
    def _get_live_stats(self):
        from apps.bookings.models import Booking
        from apps.guards.models import GuardProfile
        from apps.sos.models import SOSAlert

        return {
            "active_sessions": Booking.objects.filter(status="ACTIVE").count(),
            "guards_online": GuardProfile.objects.filter(is_online=True).count(),
            "open_sos_alerts": SOSAlert.objects.exclude(
                status__in=["RESOLVED", "FALSE_ALARM"]
            ).count(),
        }
