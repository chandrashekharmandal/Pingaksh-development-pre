from django.db import models


class DailyStats(models.Model):
    """
    Pre-aggregated daily statistics.
    Populated nightly by Celery beat task.
    Used by admin dashboard for instant stats without heavy queries.
    """

    date = models.DateField(unique=True, db_index=True)

    # Bookings
    total_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    disputed_bookings = models.PositiveIntegerField(default=0)
    hourly_bookings = models.PositiveIntegerField(default=0)
    daily_bookings = models.PositiveIntegerField(default=0)
    weekly_bookings = models.PositiveIntegerField(default=0)
    monthly_bookings = models.PositiveIntegerField(default=0)

    # Revenue
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_fees_collected = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    guard_earnings_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    refunds_issued = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Users & Guards
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    new_guards = models.PositiveIntegerField(default=0)
    active_guards = models.PositiveIntegerField(default=0)

    # Safety
    sos_alerts = models.PositiveIntegerField(default=0)
    incidents_filed = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "analytics_daily_stats"
        ordering = ["-date"]

    def __str__(self):
        return f"DailyStats {self.date}"
