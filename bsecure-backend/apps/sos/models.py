from django.db import models
from utils.models import TimeStampedModel


class SOSAlert(TimeStampedModel):
    """
    Records every SOS trigger event.
    Mission-critical — writes must be synchronous (not Celery).
    """

    TRIGGER_METHOD_CHOICES = [
        ("BUTTON", "Manual Button Press"),
        ("SHAKE", "Shake Gesture"),
        ("AUTO_CHECKIN", "Auto — Missed Check-in Escalation"),
        ("GUARD_OFFLINE", "Auto — Guard Went Offline During Session"),
        ("GUARD_DISTRESS", "Guard Distress Button"),
    ]

    STATUS_CHOICES = [
        ("TRIGGERED", "Triggered — Awaiting Acknowledgement"),
        ("ACKNOWLEDGED", "Acknowledged by Control Room"),
        ("RESPONDING", "Response Team Dispatched"),
        ("RESOLVED", "Resolved"),
        ("FALSE_ALARM", "Resolved — False Alarm"),
    ]

    user = models.ForeignKey(
        "users.UserProfile", on_delete=models.PROTECT, related_name="sos_alerts"
    )
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sos_alerts",
    )
    trigger_method = models.CharField(max_length=20, choices=TRIGGER_METHOD_CHOICES)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="TRIGGERED", db_index=True
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_accuracy_meters = models.FloatField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_sos_alerts",
        limit_choices_to={"is_staff": True},
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    recording_file = models.FileField(
        upload_to="sos/recordings/", null=True, blank=True
    )

    class Meta:
        db_table = "sos_alert"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"SOS {self.id} [{self.trigger_method}] — {self.status}"


class EmergencyContactAlert(TimeStampedModel):
    """Tracks which emergency contacts were notified for an SOS."""

    sos_alert = models.ForeignKey(
        SOSAlert, on_delete=models.CASCADE, related_name="contact_alerts"
    )
    contact_name = models.CharField(max_length=150)
    contact_phone = models.CharField(max_length=20)
    sms_sent = models.BooleanField(default=False)
    sms_delivered = models.BooleanField(default=False)
    call_attempted = models.BooleanField(default=False)

    class Meta:
        db_table = "sos_emergency_contact_alert"

    def __str__(self):
        return f"Alert to {self.contact_name} for SOS {self.sos_alert_id}"


class Incident(TimeStampedModel):
    """
    User or guard-filed incident reports.
    Separate from SOS — incidents are retrospective reports.
    """

    INCIDENT_TYPE_CHOICES = [
        ("GUARD_MISCONDUCT", "Guard Misconduct"),
        ("GUARD_NO_SHOW", "Guard Did Not Arrive"),
        ("GUARD_EARLY_DEPARTURE", "Guard Left Early"),
        ("THREATENING_BEHAVIOUR", "Threatening Behaviour"),
        ("THEFT", "Theft"),
        ("PROPERTY_DAMAGE", "Property Damage"),
        ("DANGEROUS_CLIENT", "Dangerous Client (Guard Report)"),
        ("SAFETY_CONCERN", "General Safety Concern"),
        ("OTHER", "Other"),
    ]

    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open — Under Investigation"),
        ("IN_REVIEW", "In Review"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed — No Action"),
    ]

    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.PROTECT, related_name="incidents"
    )
    filed_by = models.ForeignKey(
        "users.UserProfile", on_delete=models.PROTECT, related_name="filed_incidents"
    )
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES)
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, default="MEDIUM"
    )
    description = models.TextField()
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="OPEN", db_index=True
    )

    assigned_to = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents",
        limit_choices_to={"is_staff": True},
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sos_incident"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Incident {self.incident_type} [{self.severity}] — {self.status}"


class IncidentEvidence(TimeStampedModel):
    """Photo or video evidence attached to an incident report."""

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="evidence"
    )
    file = models.FileField(upload_to="incidents/evidence/")
    file_type = models.CharField(
        max_length=10, choices=[("IMAGE", "Image"), ("VIDEO", "Video")]
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "sos_incident_evidence"

    def __str__(self):
        return f"Evidence [{self.file_type}] for Incident {self.incident_id}"
