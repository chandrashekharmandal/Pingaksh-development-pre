"""
Phase 5b Tests — apps/guards
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserProfile
from apps.guards.models import GuardProfile, GuardAvailability
from apps.guards.services import GuardService


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def guard_user(db):
    user = UserProfile.objects.create_user(
        phone_number="+919900000010",
        full_name="Guard User",
        role="GUARD",
    )
    return user


@pytest.fixture
def guard_profile(guard_user):
    return GuardProfile.objects.create(
        user=guard_user, guard_type="UNARMED", verification_status="ACTIVE"
    )


@pytest.fixture
def auth_client(client, guard_user):
    refresh = RefreshToken.for_user(guard_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@pytest.fixture
def regular_user(db):
    return UserProfile.objects.create_user(
        phone_number="+919900000020", full_name="Regular User"
    )


@pytest.fixture
def regular_auth_client(client, regular_user):
    c = APIClient()
    refresh = RefreshToken.for_user(regular_user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


# ---------------------------------------------------------------------------
# GET /api/guards/me/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuardMeView:
    def test_get_guard_profile(self, auth_client, guard_profile):
        response = auth_client.get("/api/guards/me/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["guard_type"] == "UNARMED"

    def test_non_guard_cannot_access(self, regular_auth_client):
        response = regular_auth_client.get("/api/guards/me/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_guard_profile(self, auth_client, guard_profile):
        response = auth_client.patch(
            "/api/guards/me/",
            {"bio": "Experienced guard", "years_of_experience": 5},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["bio"] == "Experienced guard"


# ---------------------------------------------------------------------------
# PUT /api/guards/me/online-status/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestOnlineStatus:
    def test_cannot_go_online_if_not_active(self, auth_client, guard_profile):
        guard_profile.verification_status = "PENDING"
        guard_profile.save()
        response = auth_client.put(
            "/api/guards/me/online-status/",
            {"is_online": True, "latitude": 12.97, "longitude": 77.59},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_can_go_online_if_active(self, auth_client, guard_profile):
        response = auth_client.put(
            "/api/guards/me/online-status/",
            {"is_online": True, "latitude": 12.97, "longitude": 77.59},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["is_online"] is True

    def test_go_offline(self, auth_client, guard_profile):
        guard_profile.is_online = True
        guard_profile.save()
        response = auth_client.put(
            "/api/guards/me/online-status/",
            {"is_online": False},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["is_online"] is False


# ---------------------------------------------------------------------------
# GET/POST /api/guards/me/documents/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuardDocuments:
    def test_list_documents_empty(self, auth_client, guard_profile):
        response = auth_client.get("/api/guards/me/documents/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_upload_document(self, auth_client, guard_profile, tmp_path):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile(
            "id.pdf", b"fake pdf content", content_type="application/pdf"
        )
        response = auth_client.post(
            "/api/guards/me/documents/",
            {"document_type": "GOVT_ID", "file": f},
            format="multipart",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["document_type"] == "GOVT_ID"
        assert data["status"] == "UPLOADED"


# ---------------------------------------------------------------------------
# GET/PUT /api/guards/me/availability/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuardAvailability:
    def test_get_availability_empty(self, auth_client, guard_profile):
        response = auth_client.get("/api/guards/me/availability/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_set_availability(self, auth_client, guard_profile):
        payload = [
            {
                "weekday": 0,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "is_available": True,
            },
            {
                "weekday": 1,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "is_available": True,
            },
        ]
        response = auth_client.put(
            "/api/guards/me/availability/", payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == 2

    def test_replace_availability(self, auth_client, guard_profile):
        GuardAvailability.objects.create(
            guard=guard_profile, weekday=0, start_time="09:00", end_time="17:00"
        )
        payload = [
            {
                "weekday": 2,
                "start_time": "10:00:00",
                "end_time": "18:00:00",
                "is_available": True,
            }
        ]
        response = auth_client.put(
            "/api/guards/me/availability/", payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["weekday"] == 2


# ---------------------------------------------------------------------------
# GET /api/guards/{id}/  (public profile)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPublicGuardProfile:
    def test_get_public_profile(self, regular_auth_client, guard_profile):
        response = regular_auth_client.get(f"/api/guards/{guard_profile.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert "full_name" in response.json()["data"]

    def test_not_found(self, regular_auth_client):
        import uuid

        response = regular_auth_client.get(f"/api/guards/{uuid.uuid4()}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# GuardService unit tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGuardService:
    def test_get_guard_profile(self, guard_user, guard_profile):
        g = GuardService.get_guard_profile(guard_user)
        assert g == guard_profile

    def test_get_guard_profile_not_found(self, regular_user):
        from rest_framework.exceptions import NotFound

        with pytest.raises(NotFound):
            GuardService.get_guard_profile(regular_user)

    def test_update_guard_profile(self, guard_profile):
        GuardService.update_guard_profile(guard_profile, {"bio": "Test bio"})
        guard_profile.refresh_from_db()
        assert guard_profile.bio == "Test bio"

    def test_set_online_status_active_guard(self, guard_profile):
        guard_profile.verification_status = "ACTIVE"
        guard_profile.save()
        GuardService.set_online_status(guard_profile, True)
        guard_profile.refresh_from_db()
        assert guard_profile.is_online

    def test_set_online_status_non_active_raises(self, guard_profile):
        from rest_framework.exceptions import PermissionDenied

        guard_profile.verification_status = "PENDING"
        guard_profile.save()
        with pytest.raises(PermissionDenied):
            GuardService.set_online_status(guard_profile, True)
