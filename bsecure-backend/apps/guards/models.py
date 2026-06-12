from django.db import models
from utils.models import TimeStampedModel
from apps.users.models import UserProfile

# Use PostGIS PointField when GIS backend is available, fall back to plain field in tests
try:
    from django.contrib.gis.db import models as gis_models

    _PointField = gis_models.PointField
except Exception:
    _PointField = None


class GuardProfile(TimeStampedModel):
    """
    Extended profile for security guards.
    OneToOne with UserProfile (guard's base account).
    """

    GUARD_TYPE_CHOICES = [
        ("UNARMED", "Unarmed Security Guard"),
        ("ARMED", "Armed Security Guard"),
        ("FEMALE", "Female Security Guard"),
        ("CPO", "Close Protection Officer"),
        ("EVENT", "Event Security"),
        ("K9", "K9 / Dog Handler"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("PENDING", "Pending — Documents not yet uploaded"),
        ("UNDER_REVIEW", "Under Review — Admin reviewing documents"),
        ("ACTIVE", "Active — Verified and can accept bookings"),
        ("SUSPENDED", "Suspended — Temporarily deactivated"),
        ("BANNED", "Banned — Permanently deactivated"),
        ("DOCUMENTS_REJECTED", "Documents Rejected — Needs resubmission"),
    ]

    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="guard_profile"
    )

    # Professional details
    guard_type = models.CharField(
        max_length=20, choices=GUARD_TYPE_CHOICES, default="UNARMED"
    )
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(blank=True, max_length=500)
    languages_spoken = models.JSONField(default=list)
    skills = models.JSONField(default=list)

    # Verification
    verification_status = models.CharField(
        max_length=25,
        choices=VERIFICATION_STATUS_CHOICES,
        default="PENDING",
        db_index=True,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guards_verified",
        limit_choices_to={"is_staff": True},
    )

    # Live location (PostGIS — enables fast proximity queries; plain field in test)
    current_location = (
        _PointField(
            geography=True,
            null=True,
            blank=True,
            help_text="Current GPS coordinates. Updated every 3–5s when on duty.",
        )
        if _PointField is not None
        else models.TextField(null=True, blank=True)
    )
    last_location_update = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False, db_index=True)

    # Ratings (denormalized — updated via signal on new Review)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    total_sessions_completed = models.PositiveIntegerField(default=0)

    # Payout details
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_ifsc_code = models.CharField(max_length=11, blank=True)
    upi_id = models.CharField(max_length=50, blank=True)
    payout_preference = models.CharField(
        max_length=10,
        choices=[("BANK", "Bank Transfer"), ("UPI", "UPI")],
        default="UPI",
    )

    # Working preferences
    preferred_work_radius_km = models.PositiveSmallIntegerField(default=10)
    max_daily_hours = models.PositiveSmallIntegerField(default=12)

    class Meta:
        db_table = "guards_profile"
        indexes = [
            models.Index(fields=["verification_status", "is_online"]),
            models.Index(fields=["guard_type", "is_online"]),
            models.Index(fields=["average_rating"]),
        ]

    def __str__(self):
        return f"Guard: {self.user.display_name} [{self.guard_type}] — {self.verification_status}"

    @property
    def is_available(self):
        return self.is_online and self.verification_status == "ACTIVE"


class GuardDocument(TimeStampedModel):
    """
    Documents uploaded by guards for verification.
    One record per document type per guard (re-upload replaces previous).
    """

    DOCUMENT_TYPE_CHOICES = [
        ("GOVT_ID", "Government Photo ID (Aadhaar / Passport / Voter ID)"),
        ("POLICE_CERT", "Police Verification Certificate"),
        ("PSARA_LICENSE", "PSARA Security Guard License"),
        ("TRAINING_CERT", "Security Training Certificate"),
        ("ARMED_LICENSE", "Arms License (Armed Guards Only)"),
        ("PROFILE_PHOTO", "Live Profile Selfie"),
        ("ADDRESS_PROOF", "Address Proof"),
    ]

    DOCUMENT_STATUS_CHOICES = [
        ("UPLOADED", "Uploaded — Awaiting review"),
        ("UNDER_REVIEW", "Under Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected — Needs resubmission"),
        ("EXPIRED", "Expired — Renewal required"),
    ]

    guard = models.ForeignKey(
        GuardProfile, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=25, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to="guards/documents/")
    file_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=15,
        choices=DOCUMENT_STATUS_CHOICES,
        default="UPLOADED",
        db_index=True,
    )

    expiry_date = models.DateField(null=True, blank=True)
    expiry_reminder_sent = models.BooleanField(default=False)

    reviewed_by = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_reviewed",
        limit_choices_to={"is_staff": True},
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "guards_document"
        unique_together = [("guard", "document_type")]

    def __str__(self):
        return f"{self.get_document_type_display()} — {self.guard} [{self.status}]"


class GuardAvailability(TimeStampedModel):
    """
    Weekly recurring availability schedule for a guard.
    One record per weekday.
    """

    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    guard = models.ForeignKey(
        GuardProfile, on_delete=models.CASCADE, related_name="availability_schedule"
    )
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "guards_availability"
        unique_together = [("guard", "weekday")]
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.guard.user.display_name} — {self.get_weekday_display()} {self.start_time}–{self.end_time}"


class GuardBlackoutDate(TimeStampedModel):
    """Specific dates when a guard is unavailable."""

    guard = models.ForeignKey(
        GuardProfile, on_delete=models.CASCADE, related_name="blackout_dates"
    )
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "guards_blackout_date"
        unique_together = [("guard", "date")]

    def __str__(self):
        return f"{self.guard.user.display_name} — blocked {self.date}"
