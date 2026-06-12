import hashlib
import secrets

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from utils.models import TimeStampedModel
from apps.users.models import UserProfile
from apps.guards.models import GuardProfile


class Booking(TimeStampedModel):
    """
    Core booking model. Represents a single security service engagement.
    Uses django-fsm for state transition management.
    """

    SERVICE_TYPE_CHOICES = [
        ("HOURLY", "Hourly Protection"),
        ("DAILY", "Daily Protection (8h or 12h shift)"),
        ("WEEKLY", "Weekly Protection (5 or 7 days)"),
        ("MONTHLY", "Monthly Protection (30 days)"),
    ]

    GUARD_TYPE_CHOICES = [
        ("UNARMED", "Unarmed Guard"),
        ("ARMED", "Armed Guard"),
        ("FEMALE", "Female Guard"),
        ("CPO", "Close Protection Officer"),
        ("EVENT", "Event Security"),
    ]

    STATUS_CHOICES = [
        ("REQUESTED", "Requested"),
        ("BROADCAST", "Broadcasting to Guards"),
        ("ACCEPTED", "Guard Accepted"),
        ("EN_ROUTE", "Guard En Route"),
        ("ARRIVED", "Guard Arrived"),
        ("ACTIVE", "Session Active"),
        ("COMPLETED", "Session Completed"),
        ("CANCELLED", "Cancelled"),
        ("DISPUTED", "Disputed"),
        ("EXPIRED", "Expired — No Guard Found"),
    ]

    # Participants
    user = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="bookings"
    )
    guard = models.ForeignKey(
        GuardProfile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bookings",
    )

    # Service details
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)
    guard_type_requested = models.CharField(max_length=10, choices=GUARD_TYPE_CHOICES)

    # State (managed by django-fsm)
    status = FSMField(default="REQUESTED", choices=STATUS_CHOICES, db_index=True)

    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    is_immediate = models.BooleanField(default=True)

    # Session timestamps
    guard_accepted_at = models.DateTimeField(null=True, blank=True)
    guard_arrived_at = models.DateTimeField(null=True, blank=True)
    session_started_at = models.DateTimeField(null=True, blank=True)
    session_ended_at = models.DateTimeField(null=True, blank=True)

    # Location (where service is required)
    service_address = models.TextField()
    service_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    service_longitude = models.DecimalField(max_digits=9, decimal_places=6)

    # Pricing
    base_rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    promo_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    platform_fee = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    guard_earnings = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    tax_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    # OTP for session start/end verification
    start_otp_hash = models.CharField(max_length=64, blank=True)
    end_otp_hash = models.CharField(max_length=64, blank=True)

    # Cancellation
    cancelled_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_bookings",
    )
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Recurring booking support
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(null=True, blank=True)
    parent_booking = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recurrence_instances",
    )

    # Admin
    admin_notes = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False)

    class Meta:
        db_table = "bookings_booking"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["guard", "status"]),
            models.Index(fields=["status", "scheduled_start"]),
            models.Index(fields=["is_immediate", "status"]),
        ]
        ordering = ["-created_at"]

    # ─── FSM Transitions ──────────────────────────────────────────────────────

    @transition(field=status, source="REQUESTED", target="BROADCAST")
    def start_broadcast(self):
        """System starts broadcasting booking request to nearby guards."""
        pass

    @transition(field=status, source="BROADCAST", target="ACCEPTED")
    def guard_accept(self, guard: GuardProfile):
        """A guard accepts the booking."""
        self.guard = guard
        self.guard_accepted_at = timezone.now()

    @transition(field=status, source="ACCEPTED", target="EN_ROUTE")
    def guard_start_travel(self):
        """Guard begins travelling to client location."""
        pass

    @transition(field=status, source="EN_ROUTE", target="ARRIVED")
    def guard_arrive(self):
        """Guard marks themselves as arrived at client location."""
        self.guard_arrived_at = timezone.now()

    @transition(field=status, source="ARRIVED", target="ACTIVE")
    def start_session(self):
        """OTP verified — session officially starts."""
        self.session_started_at = timezone.now()

    @transition(field=status, source="ACTIVE", target="COMPLETED")
    def complete_session(self):
        """OTP verified — session ends normally."""
        self.session_ended_at = timezone.now()

    @transition(field=status, source="ACTIVE", target="DISPUTED")
    def dispute_session(self):
        """User or guard raises a dispute."""
        pass

    @transition(
        field=status,
        source=["REQUESTED", "BROADCAST", "ACCEPTED", "EN_ROUTE", "ARRIVED"],
        target="CANCELLED",
    )
    def cancel(self, cancelled_by: UserProfile, reason: str = ""):
        """Cancel booking (allowed up to session start)."""
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.cancelled_at = timezone.now()

    @transition(field=status, source="BROADCAST", target="EXPIRED")
    def expire(self):
        """No guard found within timeout window."""
        pass

    # ─── OTP helpers ──────────────────────────────────────────────────────────

    def generate_start_otp(self) -> str:
        otp = str(secrets.randbelow(10000)).zfill(4)
        self.start_otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        self.save(update_fields=["start_otp_hash"])
        return otp

    def verify_start_otp(self, otp: str) -> bool:
        return bool(
            self.start_otp_hash
            and self.start_otp_hash == hashlib.sha256(otp.encode()).hexdigest()
        )

    def generate_end_otp(self) -> str:
        otp = str(secrets.randbelow(10000)).zfill(4)
        self.end_otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        self.save(update_fields=["end_otp_hash"])
        return otp

    def verify_end_otp(self, otp: str) -> bool:
        return bool(
            self.end_otp_hash
            and self.end_otp_hash == hashlib.sha256(otp.encode()).hexdigest()
        )

    def __str__(self):
        return f"Booking {self.id} — {self.user} + {self.guard} [{self.status}]"


class BookingBroadcast(TimeStampedModel):
    """
    Tracks which guards received a booking request broadcast
    and their response (accepted, declined, timed out).
    """

    RESPONSE_CHOICES = [
        ("SENT", "Request Sent"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
        ("TIMEOUT", "No Response — Timed Out"),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="broadcasts"
    )
    guard = models.ForeignKey(
        GuardProfile, on_delete=models.CASCADE, related_name="broadcast_requests"
    )
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default="SENT")
    broadcast_radius_km = models.PositiveSmallIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "bookings_broadcast"
        unique_together = [("booking", "guard")]

    def __str__(self):
        return f"Broadcast {self.booking_id} → {self.guard} [{self.response}]"


class GuardCheckIn(TimeStampedModel):
    """
    Records guard check-ins during long active sessions.
    Missed check-ins trigger alerts to user and admin.
    """

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="checkins"
    )
    guard = models.ForeignKey(
        GuardProfile, on_delete=models.CASCADE, related_name="checkins"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    notes = models.CharField(max_length=200, blank=True)
    is_auto = models.BooleanField(default=False)

    class Meta:
        db_table = "bookings_checkin"
        ordering = ["-created_at"]

    def __str__(self):
        return f"CheckIn for booking {self.booking_id} at {self.created_at}"
