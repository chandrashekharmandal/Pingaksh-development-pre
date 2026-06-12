"""
Phase 5a Tests — apps/users
Covers: MeView, MePhotoView, AddressListCreateView/DetailView,
        EmergencyContactListCreateView/DetailView, FCMTokenView,
        AccountDeletionView, UserService
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserProfile, Address, EmergencyContact
from apps.users.services import UserService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserProfile.objects.create_user(
        phone_number="+919900000001",
        full_name="Test User",
        email="test@example.com",
    )


@pytest.fixture
def auth_client(client, user):
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# ---------------------------------------------------------------------------
# GET /api/users/me/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestMeView:
    def test_get_me_returns_profile(self, auth_client, user):
        response = auth_client.get("/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["phone_number"] == user.phone_number
        assert data["full_name"] == user.full_name
        assert "wallet_balance" in data
        assert "total_bookings" in data

    def test_get_me_requires_auth(self, client):
        response = client.get("/api/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_me_updates_profile(self, auth_client, user):
        response = auth_client.patch(
            "/api/users/me/",
            {"full_name": "Updated Name"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["full_name"] == "Updated Name"
        user.refresh_from_db()
        assert user.full_name == "Updated Name"

    def test_put_me_updates_all_fields(self, auth_client, user):
        response = auth_client.put(
            "/api/users/me/",
            {"full_name": "Full Update", "email": "new@example.com", "gender": "MALE"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["email"] == "new@example.com"


# ---------------------------------------------------------------------------
# GET/POST /api/users/me/addresses/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAddressViews:
    ADDRESS_DATA = {
        "label": "HOME",
        "line1": "42, Indiranagar 1st Cross",
        "line2": "HAL 2nd Stage",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560038",
        "latitude": "12.971600",
        "longitude": "77.594600",
        "is_default": True,
    }

    def test_list_addresses_empty(self, auth_client):
        response = auth_client.get("/api/users/me/addresses/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_create_address(self, auth_client):
        response = auth_client.post(
            "/api/users/me/addresses/", self.ADDRESS_DATA, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["city"] == "Bengaluru"
        assert data["is_default"] is True

    def test_list_addresses_after_create(self, auth_client):
        auth_client.post("/api/users/me/addresses/", self.ADDRESS_DATA, format="json")
        response = auth_client.get("/api/users/me/addresses/")
        assert len(response.json()["data"]) == 1

    def test_update_address(self, auth_client, user):
        addr = Address.objects.create(
            user=user,
            label="HOME",
            line1="Old",
            city="Old City",
            state="KA",
            pincode="560001",
        )
        response = auth_client.patch(
            f"/api/users/me/addresses/{addr.id}/",
            {"city": "Mysore"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["city"] == "Mysore"

    def test_delete_address(self, auth_client, user):
        addr = Address.objects.create(
            user=user,
            label="HOME",
            line1="To Delete",
            city="Chennai",
            state="TN",
            pincode="600001",
        )
        response = auth_client.delete(f"/api/users/me/addresses/{addr.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Address.objects.filter(id=addr.id).exists()

    def test_cannot_exceed_10_addresses(self, auth_client, user):
        for i in range(10):
            Address.objects.create(
                user=user,
                label="HOME",
                line1=f"Line {i}",
                city="City",
                state="ST",
                pincode="123456",
            )
        response = auth_client.post(
            "/api/users/me/addresses/", self.ADDRESS_DATA, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_address_of_other_user_returns_404(self, auth_client, db):
        other = UserProfile.objects.create_user(phone_number="+919900009999")
        addr = Address.objects.create(
            user=other,
            label="HOME",
            line1="Addr",
            city="C",
            state="S",
            pincode="111111",
        )
        response = auth_client.delete(f"/api/users/me/addresses/{addr.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# GET/POST /api/users/me/emergency-contacts/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmergencyContactViews:
    CONTACT_DATA = {
        "name": "Jane Doe",
        "phone_number": "+919800000002",
        "relationship": "SPOUSE",
        "is_primary": True,
    }

    def test_list_contacts_empty(self, auth_client):
        response = auth_client.get("/api/users/me/emergency-contacts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_create_contact(self, auth_client):
        response = auth_client.post(
            "/api/users/me/emergency-contacts/", self.CONTACT_DATA, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()["data"]
        assert data["name"] == "Jane Doe"
        assert data["relationship"] == "SPOUSE"

    def test_cannot_exceed_5_contacts(self, auth_client, user):
        for i in range(5):
            EmergencyContact.objects.create(
                user=user,
                name=f"Contact {i}",
                phone_number=f"+9100000000{i}",
                relationship="OTHER",
            )
        response = auth_client.post(
            "/api/users/me/emergency-contacts/", self.CONTACT_DATA, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_contact(self, auth_client, user):
        contact = EmergencyContact.objects.create(
            user=user,
            name="To Delete",
            phone_number="+919000000099",
            relationship="FRIEND",
        )
        response = auth_client.delete(f"/api/users/me/emergency-contacts/{contact.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT


# ---------------------------------------------------------------------------
# PUT /api/users/me/fcm-token/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFCMTokenView:
    def test_update_fcm_token(self, auth_client, user):
        response = auth_client.put(
            "/api/users/me/fcm-token/",
            {"fcm_token": "abc123tokenXYZ"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.fcm_token == "abc123tokenXYZ"

    def test_missing_fcm_token_returns_400(self, auth_client):
        response = auth_client.put("/api/users/me/fcm-token/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# DELETE /api/users/me/account/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAccountDeletion:
    def test_delete_account(self, auth_client, user):
        response = auth_client.delete("/api/users/me/account/")
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_deleted is True
        assert user.is_active is False

    def test_delete_account_requires_auth(self, client):
        response = client.delete("/api/users/me/account/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# UserService unit tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserService:
    def test_update_profile(self, user):
        UserService.update_profile(user, {"full_name": "New Name"})
        user.refresh_from_db()
        assert user.full_name == "New Name"

    def test_update_fcm_token(self, user):
        UserService.update_fcm_token(user, "token_xyz")
        user.refresh_from_db()
        assert user.fcm_token == "token_xyz"

    def test_request_account_deletion(self, user):
        UserService.request_account_deletion(user)
        user.refresh_from_db()
        assert user.is_deleted
        assert not user.is_active
        assert user.deleted_at is not None

    def test_create_address_service(self, user):
        addr = UserService.create_address(
            user,
            {
                "label": "HOME",
                "line1": "123 Main",
                "city": "Mumbai",
                "state": "MH",
                "pincode": "400001",
            },
        )
        assert addr.user == user
        assert addr.city == "Mumbai"

    def test_create_emergency_contact_service(self, user):
        contact = UserService.create_emergency_contact(
            user,
            {"name": "Bob", "phone_number": "+919123456789", "relationship": "FRIEND"},
        )
        assert contact.user == user
        assert contact.name == "Bob"
