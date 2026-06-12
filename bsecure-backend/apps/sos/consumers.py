import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class SOSFeedConsumer(AsyncWebsocketConsumer):
    """
    Admin-only WebSocket for real-time SOS alert feed.
    URL: /ws/sos/feed/

    All admin clients subscribe to group 'admin_sos_feed'.
    When an SOS is triggered (via REST API), it's broadcast here.
    """

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous or not user.is_staff:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add("admin_sos_feed", self.channel_name)
        await self.accept()
        logger.info(f"WS SOS feed connected: admin={user.id}")

    async def disconnect(self, close_code):
        if hasattr(self, "channel_layer"):
            await self.channel_layer.group_discard("admin_sos_feed", self.channel_name)
        logger.info(f"WS SOS feed disconnected code={close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("type") == "acknowledge_sos":
            await self._handle_acknowledge(data)

    async def sos_alert(self, event):
        """Called when a new SOS is triggered anywhere on the platform."""
        await self.send(text_data=json.dumps(event["payload"]))

    async def sos_status_update(self, event):
        """Called when SOS status changes (acknowledged, resolved)."""
        await self.send(text_data=json.dumps(event["payload"]))

    async def _handle_acknowledge(self, data):
        sos_id = data.get("sos_id")
        if not sos_id:
            return
        await database_sync_to_async(self._ack_sos)(sos_id)

    def _ack_sos(self, sos_id):
        from apps.sos.models import SOSAlert
        from django.utils import timezone

        SOSAlert.objects.filter(id=sos_id, status="TRIGGERED").update(
            status="ACKNOWLEDGED",
            acknowledged_at=timezone.now(),
            assigned_to=self.scope["user"],
        )
