"""Celery tasks for the guards app."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(queue="scheduled", name="apps.guards.tasks.check_document_expiry")
def check_document_expiry():
    """
    Daily: find guards with documents expiring within 30 days.
    Send reminder notifications and flag in admin panel.
    """
    from apps.guards.models import GuardDocument
    from apps.notifications.tasks import send_push_notification
    from django.utils import timezone
    from datetime import timedelta

    thirty_days_out = timezone.now().date() + timedelta(days=30)

    expiring_docs = GuardDocument.objects.filter(
        status="APPROVED",
        expiry_date__lte=thirty_days_out,
        expiry_date__gte=timezone.now().date(),
        expiry_reminder_sent=False,
    ).select_related("guard__user")

    count = 0
    for doc in expiring_docs:
        days_left = (doc.expiry_date - timezone.now().date()).days
        send_push_notification.delay(
            str(doc.guard.user.id),
            "Document Expiring Soon",
            f"Your {doc.document_type} expires in {days_left} days. Please renew it to stay active.",
        )
        doc.expiry_reminder_sent = True
        doc.save(update_fields=["expiry_reminder_sent"])
        count += 1

    return f"Sent expiry reminders for {count} documents"
