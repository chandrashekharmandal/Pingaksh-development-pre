"""
Phase 5c Tests — apps/bookings
"""

import decimal
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserProfile
from apps.guards.models import GuardProfile
from apps.bookings.models import Booking
from apps.bookings.services import BookingService
from apps.payments.models import Wallet


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db):
    u = UserProfile.objects.create_user(
        phone_number="+919800000100", full_name="Booking User"
    )
    wallet, _ = Wallet.objects.get_or_create(user=u)
    wallet.balance = decimal.Decimal("1000.00")
    wallet.save()
    return u


@pytest.fixture
def auth_client(user):
    c = APIClient()
    refresh = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


@pytest.fixture
def guard_user(db):
    gu = UserProfile.objects.create_user(
        phone_number="+919800000200", full_name="Guard", role="GUARD"
    )
    wallet, _ = Wallet.objects.get_or_create(user=gu)
    wallet.balance = decimal.Decimal("0.00")
    wallet.save()
    return gu


@pytest.fixture
def guard_profile(guard_user):
    return GuardProfile.objects.create(
        user=guard_user,
        guard_type="UNARMED",
        verification_status="ACTIVE",
        is_online=True,
    )


@pytest.fixture
def guard_auth_client(guard_user):
    c = APIClient()
    refresh = RefreshToken.for_user(guard_user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


BOOKING_DATA = {
    "service_type": "HOURLY",
    "guard_type_requested": "UNARMED",
    "scheduled_start": "2027-01-01T10:00:00Z",
    "scheduled_end": "2027-01-01T13:00:00Z",
    "is_immediate": False,
    "service_latitude": "12.971600",
    "service_longitude": "77.594600",
    "service_address": "42 Indiranagar, Bengaluru",
    "base_rate_per_hour": "150.00",
}


# ---------------------------------------------------------------------------
# POST /api/bookings/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateBooking:
    def test_create_booking_success(self, auth_client):
        response = auth_client.post("/api/bookings/", BOOKING_DATA, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["state"] == "REQUESTED"
        assert data["service_type"] == "HOURLY"

    def test_insufficient_balance_returns_400(self, auth_client, user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        wallet.balance = decimal.Decimal("10.00")
        wallet.save()
        response = auth_client.post("/api/bookings/", BOOKING_DATA, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["error"]["code"] == "INSUFFICIENT_BALANCE"

    def test_requires_auth(self):
        c = APIClient()
        response = c.post("/api/bookings/", BOOKING_DATA, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# GET /api/bookings/{id}/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBookingDetail:
    def test_get_booking_detail(self, auth_client, user):
        booking = _make_booking(user)
        response = auth_client.get(f"/api/bookings/{booking.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert str(response.json()["data"]["id"]) == str(booking.id)

    def test_other_user_gets_403(self, user, db):
        other = UserProfile.objects.create_user(phone_number="+919800009999")
        booking = _make_booking(other)
        c = APIClient()
        refresh = RefreshToken.for_user(user)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
        response = c.get(f"/api/bookings/{booking.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# POST /api/bookings/{id}/cancel/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCancelBooking:
    def test_cancel_booking(self, auth_client, user):
        booking = _make_booking(user)
        response = auth_client.post(
            f"/api/bookings/{booking.id}/cancel/", {"reason": "Changed mind"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["state"] == "CANCELLED"

    def test_cannot_cancel_completed(self, auth_client, user):
        booking = _make_booking(user, final_status="COMPLETED")
        response = auth_client.post(f"/api/bookings/{booking.id}/cancel/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# OTP Start/End cycle
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestOTPCycle:
    def test_generate_start_otp(self, auth_client, user, guard_profile):
        booking = _make_booking(user, guard=guard_profile, final_status="ARRIVED")
        response = auth_client.post(f"/api/bookings/{booking.id}/generate-start-otp/")
        assert response.status_code == status.HTTP_200_OK
        assert "otp" in response.json()["data"]

    def test_verify_start_otp(self, user, guard_profile, guard_auth_client):
        booking = _make_booking(user, guard=guard_profile, final_status="ARRIVED")
        otp = booking.generate_start_otp()
        response = guard_auth_client.post(
            f"/api/bookings/{booking.id}/verify-start-otp/", {"otp": otp}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["state"] == "ACTIVE"

    def test_verify_start_otp_wrong_returns_400(
        self, user, guard_profile, guard_auth_client
    ):
        booking = _make_booking(user, guard=guard_profile, final_status="ARRIVED")
        booking.generate_start_otp()
        response = guard_auth_client.post(
            f"/api/bookings/{booking.id}/verify-start-otp/", {"otp": "0000"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_full_otp_lifecycle(
        self, user, guard_profile, auth_client, guard_auth_client
    ):
        booking = _make_booking(user, guard=guard_profile, final_status="ARRIVED")
        # Generate & verify start OTP
        otp = booking.generate_start_otp()
        guard_auth_client.post(
            f"/api/bookings/{booking.id}/verify-start-otp/", {"otp": otp}
        )
        booking.refresh_from_db()
        assert booking.status == "ACTIVE"
        # Generate & verify end OTP
        otp = booking.generate_end_otp()
        response = guard_auth_client.post(
            f"/api/bookings/{booking.id}/verify-end-otp/", {"otp": otp}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["state"] == "COMPLETED"


# ---------------------------------------------------------------------------
# Guard flow: en-route, arrived
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuardFlow:
    def test_guard_en_route(self, user, guard_profile, guard_auth_client):
        booking = _make_booking(user, guard=guard_profile, final_status="ACCEPTED")
        response = guard_auth_client.post(f"/api/bookings/{booking.id}/guard-en-route/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["state"] == "EN_ROUTE"

    def test_guard_arrived(self, user, guard_profile, guard_auth_client):
        booking = _make_booking(user, guard=guard_profile, final_status="EN_ROUTE")
        response = guard_auth_client.post(f"/api/bookings/{booking.id}/guard-arrived/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["state"] == "ARRIVED"


# ---------------------------------------------------------------------------
# GET /api/bookings/active/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestActiveBooking:
    def test_no_active_booking(self, auth_client):
        response = auth_client.get("/api/bookings/active/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] is None

    def test_has_active_booking(self, auth_client, user):
        _make_booking(user)
        response = auth_client.get("/api/bookings/active/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] is not None


# ---------------------------------------------------------------------------
# BookingService unit tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBookingService:
    def test_create_booking(self, user):
        data = {
            "service_type": "HOURLY",
            "guard_type_requested": "UNARMED",
            "scheduled_start": timezone.now() + timezone.timedelta(hours=1),
            "scheduled_end": timezone.now() + timezone.timedelta(hours=4),
            "service_address": "Test Address",
            "service_latitude": "12.97",
            "service_longitude": "77.59",
            "base_rate_per_hour": decimal.Decimal("150.00"),
        }
        booking = BookingService.create_booking(user, data)
        assert booking.status == "REQUESTED"
        assert booking.user == user

    def test_cancel_booking(self, user):
        booking = _make_booking(user)
        cancelled = BookingService.cancel_booking(booking, user, "Test reason")
        assert cancelled.status == "CANCELLED"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_booking(user, guard=None, final_status="REQUESTED"):
    """Create a booking and set to the desired state directly."""
    booking = Booking.objects.create(
        user=user,
        guard=guard,
        service_type="HOURLY",
        guard_type_requested="UNARMED",
        scheduled_start=timezone.now() + timezone.timedelta(hours=1),
        scheduled_end=timezone.now() + timezone.timedelta(hours=4),
        service_address="Test Address",
        service_latitude="12.97",
        service_longitude="77.59",
        base_rate_per_hour=decimal.Decimal("150.00"),
        total_amount=decimal.Decimal("450.00"),
        platform_fee=decimal.Decimal("67.50"),
        guard_earnings=decimal.Decimal("382.50"),
    )
    if final_status != "REQUESTED":
        Booking.objects.filter(id=booking.id).update(status=final_status)
        booking.refresh_from_db()
    return booking
