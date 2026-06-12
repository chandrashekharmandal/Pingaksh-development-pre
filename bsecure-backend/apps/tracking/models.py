from django.db import models
from utils.models import TimeStampedModel

try:
    from django.contrib.gis.db import models as gis_models

    _PointField = gis_models.PointField
except Exception:
    _PointField = None


class LocationSnapshot(TimeStampedModel):
    """
    Time-series location data for guards during active sessions.
    High write volume — consider TimescaleDB for large deployments.
    Retention policy: 90 days raw, then purged.
    """

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="location_snapshots",
    )
    guard = models.ForeignKey(
        "guards.GuardProfile",
        on_delete=models.CASCADE,
        related_name="location_history",
    )

    # PostGIS point for geospatial analysis (plain field in test env)
    location = (
        _PointField(geography=True) if _PointField is not None else models.TextField()
    )
    accuracy_meters = models.FloatField(null=True, blank=True)
    speed_kmh = models.FloatField(null=True, blank=True)
    bearing_degrees = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "tracking_location_snapshot"
        indexes = [
            models.Index(fields=["booking", "timestamp"]),
            models.Index(fields=["guard", "timestamp"]),
        ]
        ordering = ["timestamp"]

    def __str__(self):
        return f"Location for booking {self.booking_id} at {self.timestamp}"
