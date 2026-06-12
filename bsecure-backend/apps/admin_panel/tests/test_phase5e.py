"""
Phase 5e Tests — notifications, SOS, reviews, admin_panel
"""

import decimal
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserProfile
from apps.guards.models import GuardProfile
from apps.notifications.models import NotificationLog
from apps.sos.models import SOSAlert, Incident
from apps.payments.models import Wallet


def make_auth_client(user):
    c = APIClient()
    refresh = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


@pytest.fixture
def user(db):
    return UserProfile.objects.create_user(
        phone_number="+919600000100", full_name="Test User"
    )


@pytest.fixture
def auth_client(user):
    return make_auth_client(user)


@pytest.fixture
def admin_user(db):
    return UserProfile.objects.create_user(
        phone_number="+919600000200",
        full_name="Admin User",
        is_staff=True,
        role="ADMIN",
    )


@pytest.fixture
def admin_client(admin_user):
    return make_auth_client(admin_user)


@pytest.fixture
def guard_user(db):
    return UserProfile.objects.create_user(phone_number="+919600000300", role="GUARD")


@pytest.fixture
def guard_profile(guard_user):
    return GuardProfile.objects.create(
        user=guard_user, guard_type="UNARMED", verification_status="PENDING"
    )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestNotifications:
    def test_list_empty(self, auth_client):
        response = auth_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_200_OK

    def test_unread_count_zero(self, auth_client):
        response = auth_client.get("/api/notifications/unread-count/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["unread_count"] == 0

    def test_unread_count_with_notifs(self, auth_client, user):
        NotificationLog.objects.create(
            recipient=user,
            channel="IN_APP",
            notification_type="TEST",
            title="Test",
            body="Test body",
        )
        response = auth_client.get("/api/notifications/unread-count/")
        assert response.json()["data"]["unread_count"] == 1

    def test_mark_read(self, auth_client, user):
        notif = NotificationLog.objects.create(
            recipient=user,
            channel="IN_APP",
            notification_type="TEST",
            title="T",
            body="B",
        )
        response = auth_client.post(f"/api/notifications/{notif.id}/read/")
        assert response.status_code == status.HTTP_200_OK
        notif.refresh_from_db()
        assert notif.is_read

    def test_mark_all_read(self, auth_client, user):
        for i in range(3):
            NotificationLog.objects.create(
                recipient=user,
                channel="IN_APP",
                notification_type="TEST",
                title=f"N{i}",
                body="B",
            )
        response = auth_client.post("/api/notifications/read-all/")
        assert response.status_code == status.HTTP_200_OK
        assert (
            NotificationLog.objects.filter(recipient=user, is_read=False).count() == 0
        )

    def test_notification_preferences(self, auth_client):
        response = auth_client.get("/api/users/me/notification-preferences/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert "push_enabled" in data

    def test_update_notification_preferences(self, auth_client):
        response = auth_client.put(
            "/api/users/me/notification-preferences/",
            {"push_enabled": False},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["push_enabled"] is False


# ---------------------------------------------------------------------------
# SOS
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSOS:
    def test_trigger_sos(self, auth_client):
        response = auth_client.post(
            "/api/sos/trigger/",
            {
                "trigger_method": "BUTTON",
                "latitude": "12.971600",
                "longitude": "77.594600",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["status"] == "TRIGGERED"
        assert "sos_id" in data

    def test_list_sos_alerts(self, auth_client, user):
        SOSAlert.objects.create(
            user=user, trigger_method="BUTTON", latitude="12.97", longitude="77.59"
        )
        response = auth_client.get("/api/sos/alerts/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == 1

    def test_sos_detail(self, auth_client, user):
        alert = SOSAlert.objects.create(
            user=user, trigger_method="BUTTON", latitude="12.97", longitude="77.59"
        )
        response = auth_client.get(f"/api/sos/alerts/{alert.id}/")
        assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReviews:
    def test_create_review_on_completed_booking(self, auth_client, user, guard_profile):
        from apps.bookings.models import Booking
        from django.utils import timezone

        booking = Booking.objects.create(
            user=user,
            guard=guard_profile,
            service_type="HOURLY",
            guard_type_requested="UNARMED",
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timezone.timedelta(hours=3),
            service_address="Test",
            service_latitude="12.97",
            service_longitude="77.59",
            base_rate_per_hour=decimal.Decimal("150.00"),
            total_amount=decimal.Decimal("450.00"),
            platform_fee=decimal.Decimal("67.50"),
            guard_earnings=decimal.Decimal("382.50"),
        )
        from apps.bookings.models import Booking as B

        B.objects.filter(id=booking.id).update(status="COMPLETED")
        response = auth_client.post(
            "/api/reviews/",
            {
                "booking_id": str(booking.id),
                "overall_rating": 5,
                "comment": "Excellent service!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_cannot_review_incomplete_booking(self, auth_client, user, guard_profile):
        from apps.bookings.models import Booking
        from django.utils import timezone

        booking = Booking.objects.create(
            user=user,
            guard=guard_profile,
            service_type="HOURLY",
            guard_type_requested="UNARMED",
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timezone.timedelta(hours=3),
            service_address="Test",
            service_latitude="12.97",
            service_longitude="77.59",
            base_rate_per_hour=decimal.Decimal("150.00"),
            total_amount=decimal.Decimal("450.00"),
            platform_fee=decimal.Decimal("67.50"),
            guard_earnings=decimal.Decimal("382.50"),
        )
        response = auth_client.post(
            "/api/reviews/",
            {"booking_id": str(booking.id), "overall_rating": 5},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Admin Panel
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAdminPanel:
    def test_dashboard_stats_admin(self, admin_client):
        response = admin_client.get("/api/admin/dashboard/stats/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert "realtime" in data
        assert "today" in data

    def test_dashboard_stats_non_admin_403(self, auth_client):
        response = auth_client.get("/api/admin/dashboard/stats/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_list(self, admin_client, user):
        response = admin_client.get("/api/admin/users/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_suspend_user(self, admin_client, user):
        response = admin_client.post(
            f"/api/admin/users/{user.id}/suspend/",
            {"reason": "Violation"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_suspended

    def test_admin_unsuspend_user(self, admin_client, user):
        user.is_suspended = True
        user.save()
        response = admin_client.post(f"/api/admin/users/{user.id}/unsuspend/")
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert not user.is_suspended

    def test_admin_credit_wallet(self, admin_client, user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        response = admin_client.post(
            f"/api/admin/users/{user.id}/credit-wallet/",
            {"amount": "100.00", "reason": "Bonus"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        wallet.refresh_from_db()
        assert wallet.balance >= decimal.Decimal("100.00")

    def test_admin_guard_list(self, admin_client, guard_profile):
        response = admin_client.get("/api/admin/guards/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_approve_guard(self, admin_client, guard_profile):
        response = admin_client.post(f"/api/admin/guards/{guard_profile.id}/approve/")
        assert response.status_code == status.HTTP_200_OK
        guard_profile.refresh_from_db()
        assert guard_profile.verification_status == "ACTIVE"

    def test_admin_sos_list(self, admin_client, user):
        SOSAlert.objects.create(
            user=user, trigger_method="BUTTON", latitude="12.97", longitude="77.59"
        )
        response = admin_client.get("/api/admin/sos/alerts/")
        assert response.status_code == status.HTTP_200_OK
