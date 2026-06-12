"""Celery tasks for the admin_panel app."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.admin_panel.tasks.push_live_dashboard_stats", queue="default")
def push_live_dashboard_stats():
    """
    Runs every 30 seconds (Celery beat).
    Collects live KPI stats and broadcasts to all connected admin WebSocket clients.
    """
    from apps.bookings.models import Booking
    from apps.guards.models import GuardProfile
    from apps.sos.models import SOSAlert
    from apps.users.models import UserProfile
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()

    stats = {
        "active_sessions": Booking.objects.filter(status="ACTIVE").count(),
        "guards_online": GuardProfile.objects.filter(is_online=True).count(),
        "open_sos_alerts": SOSAlert.objects.exclude(
            status__in=["RESOLVED", "FALSE_ALARM"]
        ).count(),
        "bookings_today": Booking.objects.filter(created_at__date=today).count(),
        "new_users_today": UserProfile.objects.filter(
            created_at__date=today, role="USER"
        ).count(),
        "timestamp": timezone.now().isoformat(),
    }

    from apps.admin_panel.consumers import AdminDashboardConsumer

    AdminDashboardConsumer.broadcast_stats_update(stats)
    return f"Live stats broadcast: {stats['active_sessions']} active sessions"
