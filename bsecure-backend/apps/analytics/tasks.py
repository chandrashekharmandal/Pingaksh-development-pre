"""Celery tasks for analytics app."""

from celery import shared_task
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(queue="low_priority", name="apps.analytics.tasks.aggregate_daily_stats")
def aggregate_daily_stats():
    """
    Nightly at midnight: aggregate stats for the previous day.
    Populates DailyStats table used by admin dashboard for fast reads.
    """
    from apps.analytics.models import DailyStats
    from apps.bookings.models import Booking
    from apps.users.models import UserProfile
    from apps.guards.models import GuardProfile
    from apps.sos.models import SOSAlert, Incident
    from apps.payments.models import Transaction
    from django.db.models import Sum

    yesterday = timezone.now().date() - timedelta(days=1)

    if DailyStats.objects.filter(date=yesterday).exists():
        return f"Stats for {yesterday} already exist"

    bookings = Booking.objects.filter(created_at__date=yesterday)
    completed = bookings.filter(status="COMPLETED")

    revenue = (
        Transaction.objects.filter(
            transaction_type="BOOKING_DEBIT",
            created_at__date=yesterday,
            status="SUCCESS",
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    platform_fees = completed.aggregate(total=Sum("platform_fee"))["total"] or 0
    guard_earnings = completed.aggregate(total=Sum("guard_earnings"))["total"] or 0

    DailyStats.objects.create(
        date=yesterday,
        total_bookings=bookings.count(),
        completed_bookings=completed.count(),
        cancelled_bookings=bookings.filter(status="CANCELLED").count(),
        gross_revenue=revenue,
        platform_fees_collected=platform_fees,
        guard_earnings_paid=guard_earnings,
        new_users=UserProfile.objects.filter(
            created_at__date=yesterday, role="USER"
        ).count(),
        new_guards=GuardProfile.objects.filter(created_at__date=yesterday).count(),
        sos_alerts=SOSAlert.objects.filter(created_at__date=yesterday).count(),
        incidents_filed=Incident.objects.filter(created_at__date=yesterday).count(),
    )

    return f"Daily stats aggregated for {yesterday}"


@shared_task(
    queue="low_priority", name="apps.analytics.tasks.cleanup_location_snapshots"
)
def cleanup_old_location_snapshots():
    """
    Weekly: delete location snapshots older than 90 days.
    """
    from apps.tracking.models import LocationSnapshot

    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = LocationSnapshot.objects.filter(timestamp__lt=cutoff).delete()
    return f"Deleted {deleted} location snapshots older than 90 days"
