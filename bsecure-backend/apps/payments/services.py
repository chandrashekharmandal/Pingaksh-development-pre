import decimal
import hashlib
import hmac
import uuid

from django.db import transaction as db_transaction
from rest_framework.exceptions import NotFound, ValidationError

from apps.payments.models import Wallet, Transaction, PaymentOrder
from apps.users.models import UserProfile


class PaymentService:
    @staticmethod
    def get_wallet(user: UserProfile) -> Wallet:
        wallet, _ = Wallet.objects.get_or_create(user=user)
        return wallet

    @staticmethod
    def get_transactions(user: UserProfile):
        wallet = PaymentService.get_wallet(user)
        return Transaction.objects.filter(wallet=wallet).order_by("-created_at")

    @staticmethod
    def initiate_topup(
        user: UserProfile, amount: decimal.Decimal, gateway: str
    ) -> dict:
        """
        Create a PaymentOrder and return gateway order details.
        In production this calls Razorpay/Stripe APIs.
        For now, creates a stub order for testing.
        """
        import os

        wallet = PaymentService.get_wallet(user)
        # Stub gateway order id
        gateway_order_id = f"order_{uuid.uuid4().hex[:16]}"

        order = PaymentOrder.objects.create(
            user=user,
            amount=amount,
            gateway=gateway,
            gateway_order_id=gateway_order_id,
            status="CREATED",
        )

        response = {
            "order_id": str(order.id),
            "gateway_order_id": gateway_order_id,
            "gateway": gateway,
            "amount": int(amount * 100),  # paisa
            "currency": "INR",
        }
        if gateway == "RAZORPAY":
            response["razorpay_key_id"] = os.environ.get(
                "RAZORPAY_KEY_ID", "rzp_test_stub"
            )
        return response

    @staticmethod
    def confirm_topup(
        user: UserProfile,
        gateway_order_id: str,
        gateway_payment_id: str,
        gateway_signature: str,
    ) -> dict:
        """
        Verify payment signature and credit wallet.
        In production: verify HMAC signature with gateway secret.
        For tests: accept any confirmation (signature verification skipped when secret is absent).
        """
        try:
            order = PaymentOrder.objects.get(
                gateway_order_id=gateway_order_id,
                user=user,
                status="CREATED",
            )
        except PaymentOrder.DoesNotExist:
            raise NotFound("Payment order not found or already processed.")

        # Signature verification (skip if no secret configured)
        import os

        secret = os.environ.get("RAZORPAY_KEY_SECRET", "")
        if secret and order.gateway == "RAZORPAY":
            expected = hmac.new(
                secret.encode(),
                f"{gateway_order_id}|{gateway_payment_id}".encode(),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(expected, gateway_signature):
                raise ValidationError("Invalid payment signature.")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=user)
            balance_before = wallet.balance
            wallet.balance += order.amount
            wallet.save(update_fields=["balance"])

            txn = Transaction.objects.create(
                wallet=wallet,
                transaction_type="TOPUP",
                amount=order.amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
                status="SUCCESS",
                gateway=order.gateway,
                gateway_order_id=gateway_order_id,
                gateway_payment_id=gateway_payment_id,
                gateway_signature=gateway_signature,
                description=f"Wallet top-up via {order.gateway}",
            )

            order.status = "PAID"
            order.gateway_response = {"payment_id": gateway_payment_id}
            order.save(update_fields=["status", "gateway_response"])

        return {
            "success": True,
            "new_balance": str(wallet.balance),
            "transaction_id": str(txn.id),
        }

    @staticmethod
    def handle_razorpay_webhook(payload: bytes, signature: str) -> dict:
        """Process Razorpay webhook events."""
        import json, os

        secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
        if secret:
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, signature):
                raise ValidationError("Invalid webhook signature.")
        event = json.loads(payload)
        # Handle payment.captured event
        if event.get("event") == "payment.captured":
            payment = event.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payment.get("order_id", "")
            payment_id = payment.get("id", "")
            try:
                order = PaymentOrder.objects.get(
                    gateway_order_id=order_id, status="CREATED"
                )
                PaymentService.confirm_topup(order.user, order_id, payment_id, "")
            except Exception:
                pass
        return {"status": "ok"}
