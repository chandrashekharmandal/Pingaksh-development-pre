from rest_framework import serializers
from .models import Wallet, Transaction, PaymentOrder, Payout


class WalletSerializer(serializers.ModelSerializer):
    available_balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Wallet
        fields = ["id", "balance", "locked_balance", "available_balance"]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "balance_before",
            "balance_after",
            "status",
            "gateway",
            "description",
            "created_at",
        ]
        read_only_fields = fields


class TopupInitiateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    gateway = serializers.ChoiceField(choices=["RAZORPAY", "STRIPE"])


class TopupConfirmSerializer(serializers.Serializer):
    gateway_order_id = serializers.CharField(max_length=100)
    gateway_payment_id = serializers.CharField(max_length=100)
    gateway_signature = serializers.CharField(max_length=256)


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id",
            "amount",
            "status",
            "period_start",
            "period_end",
            "razorpay_payout_id",
            "bank_reference",
            "processed_at",
            "created_at",
        ]
        read_only_fields = fields
