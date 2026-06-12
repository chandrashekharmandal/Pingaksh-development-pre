"""
Phase 6 WebSocket Consumer Tests

Tests for:
- TrackingConsumer (/ws/tracking/{booking_id}/)
- SOSFeedConsumer (/ws/sos/feed/)
- AdminDashboardConsumer (/ws/admin/dashboard/)

Uses channels.testing.WebsocketCommunicator with InMemoryChannelLayer.
User is injected directly into scope (no JWT needed in tests).
"""

import json
import decimal
import pytest
import pytest_asyncio

from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async

from apps.users.models import UserProfile
from apps.guards.models import GuardProfile
from apps.bookings.models import Booking
from apps.tracking.consumers import TrackingConsumer
from apps.sos.consumers import SOSFeedConsumer
from apps.admin_panel.consumers import AdminDashboardConsumer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_communicator(consumer_class, scope_overrides=None):
    """Create a WebsocketCommunicator for a consumer class with an injected user."""
    scope = {
        "type": "websocket",
        "path": "/ws/test/",
        "query_string": b"",
        "headers": [],
        "url_route": {"kwargs": {}},
        "user": AnonymousUser(),
    }
    if scope_overrides:
        scope.update(scope_overrides)
    return WebsocketCommunicator(
        consumer_class.as_asgi(), scope["path"], scope.get("headers", [])
    )


def make_tracking_communicator(user, booking_id):
    from channels.routing import URLRouter
    from django.urls import re_path

    app = URLRouter(
        [
            re_path(
                r"^ws/tracking/(?P<booking_id>[0-9a-f-]{36})/$",
                TrackingConsumer.as_asgi(),
            ),
        ]
    )
    communicator = WebsocketCommunicator(app, f"/ws/tracking/{booking_id}/")
    communicator.scope["user"] = user
    return communicator


def make_sos_communicator(user):
    from channels.routing import URLRouter
    from django.urls import re_path

    app = URLRouter(
        [
            re_path(r"^ws/sos/feed/$", SOSFeedConsumer.as_asgi()),
        ]
    )
    communicator = WebsocketCommunicator(app, "/ws/sos/feed/")
    communicator.scope["user"] = user
    return communicator


def make_admin_dashboard_communicator(user):
    from channels.routing import URLRouter
    from django.urls import re_path

    app = URLRouter(
        [
            re_path(r"^ws/admin/dashboard/$", AdminDashboardConsumer.as_asgi()),
        ]
    )
    communicator = WebsocketCommunicator(app, "/ws/admin/dashboard/")
    communicator.scope["user"] = user
    return communicator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def regular_user(db):
    return UserProfile.objects.create_user(
        phone_number="+919700000100", full_name="WS User"
    )


@pytest.fixture
def admin_user(db):
    return UserProfile.objects.create_user(
        phone_number="+919700000200",
        full_name="WS Admin",
        is_staff=True,
        role="ADMIN",
    )


@pytest.fixture
def guard_user(db):
    return UserProfile.objects.create_user(
        phone_number="+919700000300", full_name="WS Guard", role="GUARD"
    )


@pytest.fixture
def guard_profile(guard_user):
    return GuardProfile.objects.create(
        user=guard_user,
        guard_type="UNARMED",
        verification_status="ACTIVE",
    )


@pytest.fixture
def booking(regular_user, guard_profile, db):
    from django.utils import timezone

    return Booking.objects.create(
        user=regular_user,
        guard=guard_profile,
        service_type="HOURLY",
        guard_type_requested="UNARMED",
        scheduled_start=timezone.now(),
        scheduled_end=timezone.now() + timezone.timedelta(hours=2),
        service_address="Test Address",
        service_latitude=decimal.Decimal("12.971600"),
        service_longitude=decimal.Decimal("77.594600"),
        base_rate_per_hour=decimal.Decimal("150.00"),
        total_amount=decimal.Decimal("300.00"),
        platform_fee=decimal.Decimal("45.00"),
        guard_earnings=decimal.Decimal("255.00"),
    )


# ---------------------------------------------------------------------------
# SOSFeedConsumer Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestSOSFeedConsumer:
    async def test_admin_can_connect(self, admin_user):
        communicator = make_sos_communicator(admin_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    async def test_anonymous_rejected(self):
        communicator = make_sos_communicator(AnonymousUser())
        connected, code = await communicator.connect()
        assert not connected or code == 4001
        await communicator.disconnect()

    async def test_non_admin_rejected(self, regular_user):
        communicator = make_sos_communicator(regular_user)
        connected, code = await communicator.connect()
        assert not connected or code == 4001
        await communicator.disconnect()

    async def test_receives_sos_alert_broadcast(self, admin_user):
        communicator = make_sos_communicator(admin_user)
        connected, _ = await communicator.connect()
        assert connected

        # Broadcast an SOS alert to the group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "admin_sos_feed",
            {
                "type": "sos_alert",
                "payload": {
                    "event": "NEW_SOS",
                    "sos_id": "test-sos-1",
                    "trigger_method": "BUTTON",
                },
            },
        )

        response = await communicator.receive_json_from(timeout=3)
        assert response["event"] == "NEW_SOS"
        assert response["sos_id"] == "test-sos-1"

        await communicator.disconnect()

    async def test_receives_sos_status_update(self, admin_user):
        communicator = make_sos_communicator(admin_user)
        connected, _ = await communicator.connect()
        assert connected

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "admin_sos_feed",
            {
                "type": "sos_status_update",
                "payload": {
                    "event": "SOS_STATUS_CHANGE",
                    "sos_id": "test-sos-2",
                    "new_status": "ACKNOWLEDGED",
                },
            },
        )

        response = await communicator.receive_json_from(timeout=3)
        assert response["event"] == "SOS_STATUS_CHANGE"
        assert response["new_status"] == "ACKNOWLEDGED"

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# AdminDashboardConsumer Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestAdminDashboardConsumer:
    async def test_admin_can_connect(self, admin_user):
        communicator = make_admin_dashboard_communicator(admin_user)
        connected, _ = await communicator.connect()
        assert connected

        # Should receive initial_stats on connect
        response = await communicator.receive_json_from(timeout=3)
        assert response["type"] == "initial_stats"
        assert "active_sessions" in response["data"]
        assert "guards_online" in response["data"]
        assert "open_sos_alerts" in response["data"]

        await communicator.disconnect()

    async def test_anonymous_rejected(self):
        communicator = make_admin_dashboard_communicator(AnonymousUser())
        connected, code = await communicator.connect()
        assert not connected or code == 4001
        await communicator.disconnect()

    async def test_non_admin_rejected(self, regular_user):
        communicator = make_admin_dashboard_communicator(regular_user)
        connected, code = await communicator.connect()
        assert not connected or code == 4001
        await communicator.disconnect()

    async def test_receives_dashboard_update(self, admin_user):
        communicator = make_admin_dashboard_communicator(admin_user)
        connected, _ = await communicator.connect()
        assert connected

        # Consume initial_stats
        await communicator.receive_json_from(timeout=3)

        # Broadcast dashboard update
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "admin_dashboard",
            {
                "type": "dashboard_update",
                "payload": {"event": "STATS_UPDATE", "data": {"active_sessions": 5}},
            },
        )

        response = await communicator.receive_json_from(timeout=3)
        assert response["event"] == "STATS_UPDATE"
        assert response["data"]["active_sessions"] == 5

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# TrackingConsumer Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestTrackingConsumer:
    async def test_user_can_connect_to_own_booking(self, regular_user, booking):
        communicator = make_tracking_communicator(regular_user, str(booking.id))
        connected, _ = await communicator.connect()
        assert connected

        # Should receive session_state on connect
        response = await communicator.receive_json_from(timeout=3)
        assert response["type"] == "session_state"
        assert str(response["booking_id"]) == str(booking.id)

        await communicator.disconnect()

    async def test_anonymous_rejected(self, booking):
        communicator = make_tracking_communicator(AnonymousUser(), str(booking.id))
        connected, code = await communicator.connect()
        assert not connected or code == 4001
        await communicator.disconnect()

    async def test_non_participant_rejected(self, booking, db):
        outsider = await sync_to_async(UserProfile.objects.create_user)(
            phone_number="+919700000999", full_name="Outsider"
        )
        communicator = make_tracking_communicator(outsider, str(booking.id))
        connected, code = await communicator.connect()
        assert not connected or code == 4003
        await communicator.disconnect()

    async def test_guard_can_connect(self, guard_user, booking):
        communicator = make_tracking_communicator(guard_user, str(booking.id))
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_json_from(timeout=3)
        assert response["type"] == "session_state"

        await communicator.disconnect()

    async def test_non_guard_cannot_send_location(self, regular_user, booking):
        communicator = make_tracking_communicator(regular_user, str(booking.id))
        connected, _ = await communicator.connect()
        assert connected

        # Consume session_state
        await communicator.receive_json_from(timeout=3)

        # Try sending location as a regular user
        await communicator.send_json_to(
            {"type": "location_update", "lat": 12.97, "lng": 77.59}
        )

        response = await communicator.receive_json_from(timeout=3)
        assert response["type"] == "error"
        assert response["code"] == "NOT_PERMITTED"

        await communicator.disconnect()

    async def test_guard_can_send_location(self, guard_user, booking):
        communicator = make_tracking_communicator(guard_user, str(booking.id))
        connected, _ = await communicator.connect()
        assert connected

        # Consume session_state
        await communicator.receive_json_from(timeout=3)

        # Guard sends location
        await communicator.send_json_to(
            {
                "type": "location_update",
                "lat": 12.9716,
                "lng": 77.5946,
                "accuracy": 10.0,
                "speed": 0.0,
                "bearing": 0.0,
            }
        )

        # Should receive guard_location broadcast back to the session group
        response = await communicator.receive_json_from(timeout=3)
        assert response["type"] == "guard_location"
        assert response["lat"] == 12.9716
        assert response["lng"] == 77.5946

        await communicator.disconnect()

    async def test_ping_pong(self, regular_user, booking):
        communicator = make_tracking_communicator(regular_user, str(booking.id))
        connected, _ = await communicator.connect()
        assert connected

        # Consume session_state
        await communicator.receive_json_from(timeout=3)

        # Send ping as guard (connect as guard instead)
        await communicator.disconnect()

        # Connect as guard and ping
        guard_comm = make_tracking_communicator(
            await sync_to_async(lambda: booking.guard.user)(), str(booking.id)
        )
        connected, _ = await guard_comm.connect()
        assert connected
        await guard_comm.receive_json_from(timeout=3)  # session_state

        await guard_comm.send_json_to({"type": "ping"})
        response = await guard_comm.receive_json_from(timeout=3)
        assert response["type"] == "pong"

        await guard_comm.disconnect()

    async def test_nonexistent_booking_rejected(self, regular_user):
        fake_id = "00000000-0000-0000-0000-000000000000"
        communicator = make_tracking_communicator(regular_user, fake_id)
        connected, code = await communicator.connect()
        assert not connected or code == 4004
        await communicator.disconnect()

    async def test_admin_can_connect(self, admin_user, booking):
        communicator = make_tracking_communicator(admin_user, str(booking.id))
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_json_from(timeout=3)
        assert response["type"] == "session_state"

        await communicator.disconnect()
