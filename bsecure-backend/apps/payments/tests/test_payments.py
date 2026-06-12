"""
Phase 5d Tests — apps/payments
"""

import decimal
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserProfile
from apps.payments.models import Wallet, Transaction, PaymentOrder
from apps.payments.services import PaymentService


@pytest.fixture
def user(db):
    return UserProfile.objects.create_user(
        phone_number="+919700000100", full_name="Payment User"
    )


@pytest.fixture
def auth_client(user):
    c = APIClient()
    refresh = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


# ---------------------------------------------------------------------------
# GET /api/payments/wallet/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestWalletView:
    def test_get_wallet(self, auth_client, user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        wallet.balance = decimal.Decimal("250.00")
        wallet.save()
        response = auth_client.get("/api/payments/wallet/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert "wallet" in data
        assert "recent_transactions" in data
        assert data["wallet"]["balance"] == "250.00"

    def test_requires_auth(self):
        c = APIClient()
        response = c.get("/api/payments/wallet/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /api/payments/wallet/topup/initiate/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTopupInitiate:
    def test_initiate_topup(self, auth_client):
        response = auth_client.post(
            "/api/payments/wallet/topup/initiate/",
            {"amount": "500.00", "gateway": "RAZORPAY"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert "gateway_order_id" in data
        assert data["gateway"] == "RAZORPAY"
        assert data["amount"] == 50000  # paisa

    def test_invalid_amount_returns_400(self, auth_client):
        response = auth_client.post(
            "/api/payments/wallet/topup/initiate/",
            {"amount": "0", "gateway": "RAZORPAY"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# POST /api/payments/wallet/topup/confirm/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTopupConfirm:
    def test_confirm_topup(self, auth_client, user):
        # First initiate
        order = PaymentOrder.objects.create(
            user=user,
            amount=decimal.Decimal("500.00"),
            gateway="RAZORPAY",
            gateway_order_id="order_test_confirm_001",
        )
        response = auth_client.post(
            "/api/payments/wallet/topup/confirm/",
            {
                "gateway_order_id": "order_test_confirm_001",
                "gateway_payment_id": "pay_test_001",
                "gateway_signature": "sig_test",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()["data"]
        assert data["success"] is True
        assert "new_balance" in data
        assert "transaction_id" in data
        # Verify wallet was credited
        wallet = Wallet.objects.get(user=user)
        assert wallet.balance >= decimal.Decimal("500.00")

    def test_invalid_order_returns_404(self, auth_client):
        response = auth_client.post(
            "/api/payments/wallet/topup/confirm/",
            {
                "gateway_order_id": "order_nonexistent",
                "gateway_payment_id": "pay_001",
                "gateway_signature": "sig",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# GET /api/payments/transactions/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTransactionList:
    def test_list_transactions(self, auth_client, user):
        wallet, _ = Wallet.objects.get_or_create(user=user)
        Transaction.objects.create(
            wallet=wallet,
            transaction_type="TOPUP",
            amount=decimal.Decimal("100.00"),
            balance_before=decimal.Decimal("0.00"),
            balance_after=decimal.Decimal("100.00"),
            status="SUCCESS",
        )
        response = auth_client.get("/api/payments/transactions/")
        assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# PaymentService unit tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentService:
    def test_get_wallet_creates_if_missing(self, user):
        # Remove auto-created wallet
        Wallet.objects.filter(user=user).delete()
        wallet = PaymentService.get_wallet(user)
        assert wallet.user == user
        assert wallet.balance == decimal.Decimal("0.00")

    def test_initiate_topup(self, user):
        result = PaymentService.initiate_topup(
            user, decimal.Decimal("200.00"), "RAZORPAY"
        )
        assert result["gateway"] == "RAZORPAY"
        assert result["amount"] == 20000
        order = PaymentOrder.objects.get(gateway_order_id=result["gateway_order_id"])
        assert order.user == user
        assert order.status == "CREATED"

    def test_confirm_topup(self, user):
        order = PaymentOrder.objects.create(
            user=user,
            amount=decimal.Decimal("300.00"),
            gateway="RAZORPAY",
            gateway_order_id="order_svc_test_001",
        )
        result = PaymentService.confirm_topup(
            user, "order_svc_test_001", "pay_001", "sig"
        )
        assert result["success"] is True
        wallet = Wallet.objects.get(user=user)
        # Signal creates wallet with 0, we top up 300
        assert wallet.balance >= decimal.Decimal("300.00")
