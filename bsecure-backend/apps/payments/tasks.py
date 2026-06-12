"""Celery tasks for the payments app."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.payments.tasks.process_pending_payouts", queue="default")
def process_pending_payouts():
    """Process pending guard payouts — idempotent."""
    from apps.payments.models import Payout
    from django.db import transaction as db_transaction
    from django.utils import timezone

    pending = Payout.objects.filter(status="PENDING").select_related("guard__user")
    count = 0

    for payout in pending:
        try:
            with db_transaction.atomic():
                locked = Payout.objects.select_for_update(nowait=True).get(
                    id=payout.id, status="PENDING"
                )
                locked.status = "PROCESSING"
                locked.save(update_fields=["status"])

                # Actual payout via Razorpay / bank transfer — mocked here
                _execute_payout(locked)
                count += 1
        except Exception as e:
            logger.error(f"Payout {payout.id} failed: {e}")

    return f"Processed {count} payouts"


def _execute_payout(payout):
    """Execute the actual payout transfer (Razorpay Payouts API)."""
    from apps.payments.models import Payout
    from django.utils import timezone

    # In production, call Razorpay Payouts API here
    # For now, mark as COMPLETED (would be pending bank settlement in reality)
    payout.status = "COMPLETED"
    payout.processed_at = timezone.now()
    payout.save(update_fields=["status", "processed_at"])


@shared_task(queue="scheduled", name="apps.payments.tasks.process_weekly_payouts")
def process_weekly_payouts():
    """Every Friday: create pending payout records for all guards owed money."""
    from apps.payments.models import Wallet, Payout
    from apps.guards.models import GuardProfile
    from django.utils import timezone
    import decimal

    # Minimum payout threshold
    MIN_PAYOUT_AMOUNT = decimal.Decimal("100.00")

    guards = GuardProfile.objects.filter(verification_status="ACTIVE").select_related(
        "user"
    )

    count = 0
    for guard in guards:
        try:
            wallet = Wallet.objects.get(user=guard.user)
        except Wallet.DoesNotExist:
            continue

        if wallet.balance < MIN_PAYOUT_AMOUNT:
            continue

        # Avoid duplicate payouts for same period
        week_start = timezone.now().date() - timezone.timedelta(days=7)
        already_created = Payout.objects.filter(
            guard=guard,
            created_at__date__gte=week_start,
        ).exists()

        if not already_created:
            Payout.objects.create(
                guard=guard,
                amount=wallet.balance,
                status="PENDING",
            )
            count += 1

    # Trigger actual processing
    process_pending_payouts.delay()
    return f"Created {count} weekly payout records"


@shared_task(name="apps.payments.tasks.process_razorpay_event", queue="high_priority")
def process_razorpay_event(event: dict):
    """Handle a Razorpay webhook event."""
    event_type = event.get("event", "")
    logger.info(f"Razorpay event received: {event_type}")

    if event_type == "payment.captured":
        payment_id = (
            event.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
        )
        logger.info(f"Razorpay payment captured: {payment_id}")
        # TODO: update PaymentOrder status when Razorpay integration is active


@shared_task(name="apps.payments.tasks.process_stripe_event", queue="high_priority")
def process_stripe_event(event: dict):
    """Handle a Stripe webhook event."""
    event_type = event.get("type", "")
    logger.info(f"Stripe event received: {event_type}")

    if event_type == "payment_intent.succeeded":
        pi_id = event.get("data", {}).get("object", {}).get("id")
        logger.info(f"Stripe PaymentIntent succeeded: {pi_id}")
        # TODO: update PaymentOrder status when Stripe integration is active
