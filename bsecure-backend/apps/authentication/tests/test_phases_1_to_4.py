"""
Tests for phases 1–4:
- utils (helpers, validators, permissions, exceptions, pagination)
- authentication (OTPToken model, OTPService, views)
- users (UserProfile model, signals)
- JWT token flow
"""

import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        phone_number="+919876543210",
        full_name="Test User",
        role="USER",
    )


@pytest.fixture
def guard_user(db):
    user = User.objects.create_user(
        phone_number="+919999999999",
        full_name="Test Guard",
        role="GUARD",
    )
    from apps.guards.models import GuardProfile

    GuardProfile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        phone_number="+910000000001",
        password="adminpass123",
    )


@pytest.fixture
def auth_client(regular_user):
    client = APIClient()
    refresh = RefreshToken.for_user(regular_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@pytest.fixture
def guard_auth_client(guard_user):
    client = APIClient()
    from apps.guards.models import GuardProfile

    guard_user.guard_profile.verification_status = "ACTIVE"
    guard_user.guard_profile.save()
    refresh = RefreshToken.for_user(guard_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@pytest.fixture
def admin_auth_client(admin_user):
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# ─── utils/helpers.py ────────────────────────────────────────────────────────


class TestHelpers:
    def test_generate_otp_length(self):
        from utils.helpers import generate_secure_otp

        otp = generate_secure_otp(6)
        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_is_zero_padded(self):
        from utils.helpers import generate_secure_otp

        for _ in range(20):
            otp = generate_secure_otp(6)
            assert len(otp) == 6

    def test_hash_and_verify_otp(self):
        from utils.helpers import hash_otp, verify_otp

        otp = "482619"
        hashed = hash_otp(otp)
        assert len(hashed) == 64
        assert verify_otp(otp, hashed) is True
        assert verify_otp("000000", hashed) is False

    def test_mask_phone_number(self):
        from utils.helpers import mask_phone_number

        assert mask_phone_number("+919876543210") == "+91*****3210"

    def test_haversine_distance(self):
        from utils.helpers import haversine_distance_km, is_within_radius

        # Bangalore to Mumbai ≈ 840 km
        dist = haversine_distance_km(12.9716, 77.5946, 19.0760, 72.8777)
        assert 800 < dist < 900

        assert is_within_radius(12.9716, 77.5946, 12.9800, 77.6000, 5) is True
        assert is_within_radius(12.9716, 77.5946, 19.0760, 72.8777, 5) is False

    def test_calculate_booking_price(self):
        from utils.helpers import calculate_booking_price

        result = calculate_booking_price(
            base_rate_per_hour=150.0,
            duration_hours=3.0,
            platform_fee_percent=15.0,
            tax_percent=18.0,
        )
        assert result["subtotal"] == 450.0
        assert result["platform_fee"] == round(450 * 0.15, 2)
        assert result["total_amount"] > result["subtotal"]  # tax added
        assert result["guard_earnings"] < result["subtotal"]  # platform cut
        # Total = subtotal + tax on platform fee
        expected_tax = round(result["platform_fee"] * 0.18, 2)
        assert result["tax_amount"] == expected_tax


# ─── utils/validators.py ─────────────────────────────────────────────────────


class TestValidators:
    def test_valid_phone(self):
        from utils.validators import validate_indian_phone_number

        validate_indian_phone_number("+919876543210")  # should not raise

    def test_invalid_phone(self):
        from django.core.exceptions import ValidationError
        from utils.validators import validate_indian_phone_number

        with pytest.raises(ValidationError):
            validate_indian_phone_number("9876543210")  # missing +

    def test_valid_pincode(self):
        from utils.validators import validate_pincode

        validate_pincode("560038")

    def test_invalid_pincode(self):
        from django.core.exceptions import ValidationError
        from utils.validators import validate_pincode

        with pytest.raises(ValidationError):
            validate_pincode("56003")  # only 5 digits


# ─── utils/exceptions.py ─────────────────────────────────────────────────────


class TestExceptionHandler:
    def test_service_exception_attributes(self):
        from utils.exceptions import InsufficientBalanceError

        exc = InsufficientBalanceError("Not enough funds")
        assert exc.code == "INSUFFICIENT_BALANCE"
        assert exc.message == "Not enough funds"

    def test_custom_exception_handler_wraps_drf_errors(self):
        from utils.exceptions import custom_exception_handler
        from rest_framework.exceptions import NotFound
        from unittest.mock import MagicMock

        context = MagicMock()
        response = custom_exception_handler(NotFound("Not found"), context)
        assert response is not None
        assert "error" in response.data
        assert response.data["error"]["code"] == "NOT_FOUND"


# ─── utils/permissions.py ────────────────────────────────────────────────────


class TestPermissions:
    @pytest.mark.django_db
    def test_is_verified_user_passes_active_user(self, regular_user):
        from utils.permissions import IsVerifiedUser
        from unittest.mock import MagicMock

        request = MagicMock()
        request.user = regular_user
        perm = IsVerifiedUser()
        assert perm.has_permission(request, None) is True

    @pytest.mark.django_db
    def test_is_verified_user_fails_suspended(self, regular_user):
        from utils.permissions import IsVerifiedUser
        from unittest.mock import MagicMock

        regular_user.is_suspended = True
        request = MagicMock()
        request.user = regular_user
        perm = IsVerifiedUser()
        assert perm.has_permission(request, None) is False

    @pytest.mark.django_db
    def test_is_guard_fails_non_guard(self, regular_user):
        from utils.permissions import IsGuard
        from unittest.mock import MagicMock

        request = MagicMock()
        request.user = regular_user
        perm = IsGuard()
        assert perm.has_permission(request, None) is False

    @pytest.mark.django_db
    def test_is_admin_passes_staff(self, admin_user):
        from utils.permissions import IsAdminUser
        from unittest.mock import MagicMock

        request = MagicMock()
        request.user = admin_user
        perm = IsAdminUser()
        assert perm.has_permission(request, None) is True

    @pytest.mark.django_db
    def test_is_admin_fails_regular_user(self, regular_user):
        from utils.permissions import IsAdminUser
        from unittest.mock import MagicMock

        request = MagicMock()
        request.user = regular_user
        perm = IsAdminUser()
        assert perm.has_permission(request, None) is False


# ─── users/models.py ─────────────────────────────────────────────────────────


class TestUserProfile:
    @pytest.mark.django_db
    def test_create_user(self):
        user = User.objects.create_user(phone_number="+911234567890")
        assert user.pk is not None
        assert str(user.id) != ""
        assert user.role == "USER"
        assert user.is_active is True
        assert user.is_suspended is False

    @pytest.mark.django_db
    def test_uuid_primary_key(self):
        user = User.objects.create_user(phone_number="+911111111111")
        assert isinstance(user.id, uuid.UUID)

    @pytest.mark.django_db
    def test_display_name_fallback(self):
        user = User.objects.create_user(phone_number="+912222222222")
        assert user.display_name == "+912222222222"
        user.full_name = "Alice"
        assert user.display_name == "Alice"

    @pytest.mark.django_db
    def test_is_guard_property(self):
        user = User.objects.create_user(phone_number="+913333333333", role="GUARD")
        assert user.is_guard is True
        user.role = "USER"
        assert user.is_guard is False

    @pytest.mark.django_db
    def test_wallet_auto_created_on_user_creation(self):
        """Signal should auto-create wallet when user is created."""
        from apps.payments.models import Wallet

        user = User.objects.create_user(phone_number="+914444444444")
        assert Wallet.objects.filter(user=user).exists()

    @pytest.mark.django_db
    def test_notification_preferences_auto_created(self):
        """Signal should auto-create notification preferences."""
        from apps.notifications.models import NotificationPreference

        user = User.objects.create_user(phone_number="+915555555555")
        assert NotificationPreference.objects.filter(user=user).exists()

    @pytest.mark.django_db
    def test_address_default_constraint(self, regular_user):
        from apps.users.models import Address

        addr1 = Address.objects.create(
            user=regular_user,
            label="HOME",
            line1="A",
            city="B",
            state="C",
            pincode="560001",
            is_default=True,
        )
        addr2 = Address.objects.create(
            user=regular_user,
            label="OFFICE",
            line1="X",
            city="Y",
            state="Z",
            pincode="560002",
            is_default=True,
        )
        addr1.refresh_from_db()
        # addr1 should no longer be default
        assert addr1.is_default is False
        assert addr2.is_default is True


# ─── authentication/models.py ────────────────────────────────────────────────


class TestOTPToken:
    @pytest.mark.django_db
    def test_otp_token_creation(self):
        from apps.authentication.models import OTPToken

        token = OTPToken.objects.create(
            phone_number="+919876543210",
            otp_hash="abc123",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        assert token.pk is not None
        assert token.is_used is False
        assert token.is_expired is False

    @pytest.mark.django_db
    def test_otp_token_expired(self):
        from apps.authentication.models import OTPToken

        token = OTPToken.objects.create(
            phone_number="+919876543210",
            otp_hash="abc123",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        assert token.is_expired is True

    @pytest.mark.django_db
    def test_otp_token_locked_after_max_attempts(self):
        from apps.authentication.models import OTPToken
        from django.conf import settings

        token = OTPToken.objects.create(
            phone_number="+919876543210",
            otp_hash="abc123",
            expires_at=timezone.now() + timedelta(minutes=5),
            failed_attempts=settings.OTP_MAX_ATTEMPTS,
        )
        assert token.is_locked is True


# ─── authentication/services.py ──────────────────────────────────────────────


class TestOTPService:
    @pytest.mark.django_db
    @patch("apps.authentication.services.OTPService._dispatch_otp")
    def test_send_otp_creates_token(self, mock_dispatch):
        from apps.authentication.services import OTPService
        from apps.authentication.models import OTPToken

        OTPService.send_otp("+919876543210", role="USER")
        assert OTPToken.objects.filter(
            phone_number="+919876543210", is_used=False
        ).exists()
        mock_dispatch.assert_called_once()

    @pytest.mark.django_db
    @patch("apps.authentication.services.OTPService._dispatch_otp")
    def test_send_otp_invalidates_previous_tokens(self, mock_dispatch):
        from apps.authentication.services import OTPService
        from apps.authentication.models import OTPToken

        OTPService.send_otp("+919876543210")
        OTPService.send_otp("+919876543210")
        used = OTPToken.objects.filter(phone_number="+919876543210", is_used=True)
        active = OTPToken.objects.filter(phone_number="+919876543210", is_used=False)
        assert used.count() == 1
        assert active.count() == 1

    @pytest.mark.django_db
    def test_verify_otp_success_creates_user(self, db):
        from apps.authentication.models import OTPToken
        from utils.helpers import hash_otp
        from apps.authentication.services import OTPService

        phone = "+919876540001"
        otp_code = "123456"
        OTPToken.objects.create(
            phone_number=phone,
            otp_hash=hash_otp(otp_code),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        user, is_new = OTPService.verify_otp(phone, otp_code)
        assert user is not None
        assert is_new is True
        assert user.phone_number == phone

    @pytest.mark.django_db
    def test_verify_otp_wrong_code_raises(self, db):
        from apps.authentication.models import OTPToken
        from utils.helpers import hash_otp
        from apps.authentication.services import OTPService
        from utils.exceptions import OTPInvalidError

        phone = "+919876540002"
        OTPToken.objects.create(
            phone_number=phone,
            otp_hash=hash_otp("999999"),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        with pytest.raises(OTPInvalidError):
            OTPService.verify_otp(phone, "111111")

    @pytest.mark.django_db
    def test_verify_otp_expired_raises(self, db):
        from apps.authentication.models import OTPToken
        from utils.helpers import hash_otp
        from apps.authentication.services import OTPService
        from utils.exceptions import OTPExpiredError

        phone = "+919876540003"
        OTPToken.objects.create(
            phone_number=phone,
            otp_hash=hash_otp("111111"),
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        with pytest.raises(OTPExpiredError):
            OTPService.verify_otp(phone, "111111")


# ─── authentication/views.py (API tests) ─────────────────────────────────────


class TestSendOTPView:
    @pytest.mark.django_db
    @patch("apps.authentication.services.OTPService._dispatch_otp")
    def test_send_otp_returns_200(self, mock_dispatch, api_client):
        response = api_client.post(
            "/api/auth/send-otp/",
            {
                "phone_number": "+919876543210",
                "role": "USER",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "expires_in" in response.data["data"]

    @pytest.mark.django_db
    def test_send_otp_invalid_phone_returns_400(self, api_client):
        response = api_client.post(
            "/api/auth/send-otp/",
            {
                "phone_number": "not-a-phone",
                "role": "USER",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_send_otp_missing_phone_returns_400(self, api_client):
        response = api_client.post("/api/auth/send-otp/", {"role": "USER"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestVerifyOTPView:
    @pytest.mark.django_db
    def test_verify_otp_success(self, api_client, db):
        from apps.authentication.models import OTPToken
        from utils.helpers import hash_otp

        phone = "+919876540010"
        otp_code = "482619"
        OTPToken.objects.create(
            phone_number=phone,
            otp_hash=hash_otp(otp_code),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        response = api_client.post(
            "/api/auth/verify-otp/",
            {
                "phone_number": phone,
                "otp_code": otp_code,
                "role": "USER",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert "access" in data
        assert "refresh" in data
        assert data["is_new_user"] is True

    @pytest.mark.django_db
    def test_verify_otp_wrong_code_returns_400(self, api_client, db):
        from apps.authentication.models import OTPToken
        from utils.helpers import hash_otp

        phone = "+919876540011"
        OTPToken.objects.create(
            phone_number=phone,
            otp_hash=hash_otp("999999"),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        response = api_client.post(
            "/api/auth/verify-otp/",
            {
                "phone_number": phone,
                "otp_code": "111111",
                "role": "USER",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"]["code"] == "OTP_INVALID"

    @pytest.mark.django_db
    def test_verify_otp_existing_user_is_not_new(self, api_client, db):
        from apps.authentication.models import OTPToken
        from utils.helpers import hash_otp

        phone = "+919876540012"
        User.objects.create_user(phone_number=phone)
        otp_code = "654321"
        OTPToken.objects.create(
            phone_number=phone,
            otp_hash=hash_otp(otp_code),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        response = api_client.post(
            "/api/auth/verify-otp/",
            {
                "phone_number": phone,
                "otp_code": otp_code,
                "role": "USER",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["is_new_user"] is False


class TestLogoutView:
    @pytest.mark.django_db
    def test_logout_blacklists_refresh_token(self, auth_client, regular_user):
        refresh = RefreshToken.for_user(regular_user)
        response = auth_client.post(
            "/api/auth/logout/",
            {
                "refresh": str(refresh),
            },
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_logout_requires_auth(self, api_client, regular_user):
        refresh = RefreshToken.for_user(regular_user)
        response = api_client.post(
            "/api/auth/logout/",
            {
                "refresh": str(refresh),
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_logout_invalid_token_returns_400(self, auth_client):
        response = auth_client.post(
            "/api/auth/logout/",
            {
                "refresh": "invalid-token-string",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTokenRefreshView:
    @pytest.mark.django_db
    def test_refresh_returns_new_access_token(self, api_client, regular_user):
        refresh = RefreshToken.for_user(regular_user)
        response = api_client.post(
            "/api/auth/refresh/",
            {
                "refresh": str(refresh),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


# ─── Health Check ─────────────────────────────────────────────────────────────


class TestHealthCheck:
    @pytest.mark.django_db
    def test_health_check_returns_status(self, api_client):
        with patch("apps.core.views.redis") as mock_redis:
            mock_redis.from_url.return_value.ping.return_value = True
            response = api_client.get("/api/health/")
        assert response.status_code in (200, 503)
        assert "status" in response.data
        assert "db" in response.data


# ─── Booking FSM (model-level) ────────────────────────────────────────────────


class TestBookingFSM:
    @pytest.mark.django_db
    def test_booking_state_transitions(self, regular_user, guard_user):
        from apps.bookings.models import Booking
        from apps.guards.models import GuardProfile

        guard_profile = guard_user.guard_profile

        booking = Booking.objects.create(
            user=regular_user,
            service_type="HOURLY",
            guard_type_requested="UNARMED",
            scheduled_start=timezone.now() + timedelta(hours=1),
            scheduled_end=timezone.now() + timedelta(hours=4),
            service_address="Test Address",
            service_latitude="12.9716",
            service_longitude="77.5946",
            base_rate_per_hour="150.00",
        )
        assert booking.status == "REQUESTED"

        booking.start_broadcast()
        booking.save()
        assert booking.status == "BROADCAST"

        booking.guard_accept(guard=guard_profile)
        booking.save()
        assert booking.status == "ACCEPTED"
        assert booking.guard == guard_profile

        booking.guard_start_travel()
        booking.save()
        assert booking.status == "EN_ROUTE"

        booking.guard_arrive()
        booking.save()
        assert booking.status == "ARRIVED"
        assert booking.guard_arrived_at is not None

        booking.start_session()
        booking.save()
        assert booking.status == "ACTIVE"
        assert booking.session_started_at is not None

        booking.complete_session()
        booking.save()
        assert booking.status == "COMPLETED"
        assert booking.session_ended_at is not None

    @pytest.mark.django_db
    def test_booking_otp_verification(self, regular_user):
        from apps.bookings.models import Booking

        booking = Booking.objects.create(
            user=regular_user,
            service_type="HOURLY",
            guard_type_requested="UNARMED",
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=3),
            service_address="Test",
            service_latitude="12.9716",
            service_longitude="77.5946",
            base_rate_per_hour="150.00",
        )
        otp = booking.generate_start_otp()
        assert len(otp) == 4
        assert booking.verify_start_otp(otp) is True
        assert booking.verify_start_otp("0000") is False

    @pytest.mark.django_db
    def test_booking_cancel_transition(self, regular_user):
        from apps.bookings.models import Booking

        booking = Booking.objects.create(
            user=regular_user,
            service_type="HOURLY",
            guard_type_requested="UNARMED",
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=3),
            service_address="Test",
            service_latitude="12.9716",
            service_longitude="77.5946",
            base_rate_per_hour="150.00",
        )
        booking.start_broadcast()
        booking.cancel(cancelled_by=regular_user, reason="Changed my mind")
        assert booking.status == "CANCELLED"
        assert booking.cancelled_by == regular_user
        assert booking.cancellation_reason == "Changed my mind"


# ─── Reviews signal ──────────────────────────────────────────────────────────


class TestReviewSignal:
    @pytest.mark.django_db
    def test_review_updates_guard_average_rating(self, regular_user, guard_user):
        from apps.bookings.models import Booking
        from apps.reviews.models import Review
        from apps.guards.models import GuardProfile

        guard_profile = guard_user.guard_profile

        booking = Booking.objects.create(
            user=regular_user,
            guard=guard_profile,
            service_type="HOURLY",
            guard_type_requested="UNARMED",
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=3),
            service_address="Test",
            service_latitude="12.9716",
            service_longitude="77.5946",
            base_rate_per_hour="150.00",
        )

        Review.objects.create(
            booking=booking,
            reviewer=regular_user,
            guard=guard_profile,
            overall_rating=5,
        )

        guard_profile.refresh_from_db()
        assert guard_profile.average_rating == 5
        assert guard_profile.total_reviews == 1
