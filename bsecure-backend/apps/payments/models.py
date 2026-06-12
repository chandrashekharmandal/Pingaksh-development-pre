from django.db import models
from django.core.validators import MinValueValidator
from utils.models import TimeStampedModel


class Wallet(TimeStampedModel):
    """In-app wallet for users. Guards' earnings are tracked via Payout model."""

    user = models.OneToOneField(
        "users.UserProfile", on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )
    locked_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        db_table = "payments_wallet"

    @property
    def available_balance(self):
        return self.balance - self.locked_balance

    def __str__(self):
        return f"Wallet of {self.user} — ₹{self.balance}"


class Transaction(TimeStampedModel):
    """
    Immutable ledger of all wallet movements.
    Never update a transaction — only create new ones.
    """

    TRANSACTION_TYPE_CHOICES = [
        ("TOPUP", "Wallet Top-up"),
        ("BOOKING_DEBIT", "Booking Payment"),
        ("BOOKING_LOCK", "Amount Locked for Booking"),
        ("BOOKING_UNLOCK", "Amount Unlocked (Cancellation)"),
        ("REFUND", "Refund"),
        ("PROMO_CREDIT", "Promotional Credit"),
        ("REFERRAL_BONUS", "Referral Bonus"),
        ("ADMIN_CREDIT", "Admin Manual Credit"),
        ("ADMIN_DEBIT", "Admin Manual Debit"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    wallet = models.ForeignKey(
        Wallet, on_delete=models.PROTECT, related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Always positive
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    gateway = models.CharField(
        max_length=20,
        choices=[
            ("RAZORPAY", "Razorpay"),
            ("STRIPE", "Stripe"),
            ("INTERNAL", "Internal"),
        ],
        default="INTERNAL",
    )
    gateway_order_id = models.CharField(max_length=100, blank=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    gateway_signature = models.CharField(max_length=256, blank=True)

    description = models.CharField(max_length=255, blank=True)
    admin_note = models.TextField(blank=True)

    class Meta:
        db_table = "payments_transaction"
        indexes = [
            models.Index(fields=["wallet", "created_at"]),
            models.Index(fields=["booking", "transaction_type"]),
            models.Index(fields=["gateway_payment_id"]),
            models.Index(fields=["status", "transaction_type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount} [{self.status}]"


class PaymentOrder(TimeStampedModel):
    """
    Represents a payment initiation with a payment gateway.
    Created before payment; updated via webhook on completion.
    """

    STATUS_CHOICES = [
        ("CREATED", "Created at Gateway"),
        ("ATTEMPTED", "Payment Attempted"),
        ("PAID", "Successfully Paid"),
        ("FAILED", "Payment Failed"),
        ("EXPIRED", "Order Expired"),
    ]

    user = models.ForeignKey(
        "users.UserProfile", on_delete=models.PROTECT, related_name="payment_orders"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    purpose = models.CharField(
        max_length=20,
        choices=[
            ("WALLET_TOPUP", "Wallet Top-up"),
            ("BOOKING", "Direct Booking Payment"),
        ],
        default="WALLET_TOPUP",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="CREATED")
    gateway = models.CharField(
        max_length=20,
        choices=[("RAZORPAY", "Razorpay"), ("STRIPE", "Stripe")],
    )
    gateway_order_id = models.CharField(max_length=100, unique=True)
    gateway_response = models.JSONField(null=True, blank=True)
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "payments_order"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["gateway_order_id"]),
        ]

    def __str__(self):
        return f"PaymentOrder ₹{self.amount} via {self.gateway} [{self.status}]"


class Payout(TimeStampedModel):
    """Tracks earnings payouts to guards. Created per payout cycle."""

    STATUS_CHOICES = [
        ("PENDING", "Pending Approval"),
        ("PROCESSING", "Processing Transfer"),
        ("COMPLETED", "Transfer Completed"),
        ("FAILED", "Transfer Failed"),
        ("ON_HOLD", "On Hold — Under Review"),
    ]

    guard = models.ForeignKey(
        "guards.GuardProfile", on_delete=models.PROTECT, related_name="payouts"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    period_start = models.DateField()
    period_end = models.DateField()

    razorpay_payout_id = models.CharField(max_length=100, blank=True)
    bank_reference = models.CharField(max_length=100, blank=True)

    failure_reason = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payouts",
        limit_choices_to={"is_staff": True},
    )

    bookings = models.ManyToManyField(
        "bookings.Booking", blank=True, related_name="payouts"
    )

    class Meta:
        db_table = "payments_payout"
        indexes = [
            models.Index(fields=["guard", "status"]),
            models.Index(fields=["status", "period_start"]),
        ]

    def __str__(self):
        return f"Payout ₹{self.amount} for {self.guard} [{self.status}]"
