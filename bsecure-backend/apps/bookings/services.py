import decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.bookings.models import Booking, GuardCheckIn
from apps.guards.models import GuardProfile
from apps.users.models import UserProfile
from utils.exceptions import InsufficientBalanceError, NoGuardsAvailableError


class BookingService:
    @staticmethod
    def broadcast_status_change(booking):
        """
        Broadcast booking status change to all WebSocket clients in the session group.
        Called after any booking state transition.
        """
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            group_name = f"session_{booking.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "session_status_update",
                    "status": booking.status,
                    "timestamp": timezone.now().isoformat(),
                },
            )
        except Exception:
            pass  # Never let WS broadcast fail a state transition

    @staticmethod
    def create_booking(user: UserProfile, validated_data: dict) -> Booking:
        """
        Create a new booking:
        1. Calculate estimated amount
        2. Check wallet balance
        3. Create booking in REQUESTED state
        4. Transition to BROADCAST (defer actual guard matching to Celery)
        """
        from apps.payments.models import Wallet

        service_type = validated_data["service_type"]
        scheduled_start = validated_data["scheduled_start"]
        scheduled_end = validated_data["scheduled_end"]
        base_rate = validated_data.get("base_rate_per_hour", decimal.Decimal("150.00"))

        # Calculate duration & estimated amount
        duration_hours = (scheduled_end - scheduled_start).total_seconds() / 3600
        estimated_amount = decimal.Decimal(str(base_rate)) * decimal.Decimal(
            str(round(duration_hours, 2))
        )
        platform_fee = estimated_amount * decimal.Decimal("0.15")
        guard_earnings = estimated_amount - platform_fee

        # Check wallet balance
        from apps.payments.models import Wallet as WalletModel

        try:
            wallet = WalletModel.objects.get(user=user)
        except Exception:
            raise InsufficientBalanceError(
                f"Your wallet balance (₹0) is insufficient for this booking (₹{estimated_amount}). Please top up."
            )
        if wallet.balance < estimated_amount:
            raise InsufficientBalanceError(
                f"Your wallet balance (₹{wallet.balance}) is insufficient for this booking "
                f"(₹{estimated_amount}). Please top up."
            )

        with transaction.atomic():
            booking = Booking.objects.create(
                user=user,
                service_type=service_type,
                guard_type_requested=validated_data["guard_type_requested"],
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                is_immediate=validated_data.get("is_immediate", True),
                service_address=validated_data["service_address"],
                service_latitude=validated_data["service_latitude"],
                service_longitude=validated_data["service_longitude"],
                base_rate_per_hour=base_rate,
                total_amount=estimated_amount,
                platform_fee=platform_fee,
                guard_earnings=guard_earnings,
                status="REQUESTED",
            )
        return booking

    @staticmethod
    def cancel_booking(
        booking: Booking, cancelled_by: UserProfile, reason: str = ""
    ) -> Booking:
        if booking.status in ("COMPLETED", "CANCELLED", "EXPIRED", "DISPUTED"):
            raise ValidationError(
                f"Cannot cancel a booking in '{booking.status}' state."
            )
        if (
            booking.user != cancelled_by
            and not (booking.guard and booking.guard.user == cancelled_by)
            and not cancelled_by.is_staff
        ):
            raise PermissionDenied("You are not a participant in this booking.")
        booking.cancel(cancelled_by=cancelled_by, reason=reason)
        booking.save()
        return booking

    @staticmethod
    def get_booking(booking_id, user: UserProfile) -> Booking:
        try:
            booking = Booking.objects.select_related("user", "guard__user").get(
                id=booking_id
            )
        except Booking.DoesNotExist:
            raise NotFound("Booking not found.")
        # Participants or staff can view
        is_participant = (
            booking.user == user
            or (booking.guard and booking.guard.user == user)
            or user.is_staff
        )
        if not is_participant:
            raise PermissionDenied("You are not a participant in this booking.")
        return booking

    @staticmethod
    def generate_start_otp(booking: Booking, user: UserProfile) -> str:
        if booking.user != user:
            raise PermissionDenied("Only the booking user can generate the start OTP.")
        if booking.status != "ARRIVED":
            raise ValidationError(
                "Start OTP can only be generated when the guard has arrived."
            )
        otp = booking.generate_start_otp()
        return otp

    @staticmethod
    def verify_start_otp(
        booking: Booking, guard_user: UserProfile, otp: str
    ) -> Booking:
        if not booking.guard or booking.guard.user != guard_user:
            raise PermissionDenied("Only the assigned guard can verify the start OTP.")
        if booking.status != "ARRIVED":
            raise ValidationError(
                "Start OTP can only be verified when the guard has arrived."
            )
        if not booking.verify_start_otp(otp):
            raise ValidationError("Invalid OTP.")
        booking.start_session()
        booking.save()
        return booking

    @staticmethod
    def generate_end_otp(booking: Booking, user: UserProfile) -> str:
        if booking.user != user:
            raise PermissionDenied("Only the booking user can generate the end OTP.")
        if booking.status != "ACTIVE":
            raise ValidationError(
                "End OTP can only be generated during an active session."
            )
        otp = booking.generate_end_otp()
        return otp

    @staticmethod
    def verify_end_otp(booking: Booking, guard_user: UserProfile, otp: str) -> Booking:
        if not booking.guard or booking.guard.user != guard_user:
            raise PermissionDenied("Only the assigned guard can verify the end OTP.")
        if booking.status != "ACTIVE":
            raise ValidationError(
                "End OTP can only be verified during an active session."
            )
        if not booking.verify_end_otp(otp):
            raise ValidationError("Invalid OTP.")
        booking.complete_session()
        booking.save()
        # Update guard stats
        booking.guard.total_sessions_completed += 1
        booking.guard.save(update_fields=["total_sessions_completed"])
        # Credit guard earnings to wallet
        BookingService._credit_guard_earnings(booking)
        return booking

    @staticmethod
    def _credit_guard_earnings(booking: Booking):
        from apps.payments.models import Wallet, Transaction

        try:
            wallet = Wallet.objects.get(user=booking.guard.user)
            earnings = booking.guard_earnings or decimal.Decimal("0")
            balance_before = wallet.balance
            wallet.balance += earnings
            wallet.save(update_fields=["balance"])
            Transaction.objects.create(
                wallet=wallet,
                transaction_type="TOPUP",
                amount=earnings,
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=f"Earnings for booking {booking.id}",
                status="SUCCESS",
            )
        except Exception:
            pass

    @staticmethod
    def guard_en_route(booking: Booking, guard_user: UserProfile) -> Booking:
        if not booking.guard or booking.guard.user != guard_user:
            raise PermissionDenied("Only the assigned guard can update this booking.")
        if booking.status != "ACCEPTED":
            raise ValidationError("Guard can only go en-route from ACCEPTED state.")
        booking.guard_start_travel()
        booking.save()
        return booking

    @staticmethod
    def guard_arrived(booking: Booking, guard_user: UserProfile) -> Booking:
        if not booking.guard or booking.guard.user != guard_user:
            raise PermissionDenied("Only the assigned guard can update this booking.")
        if booking.status != "EN_ROUTE":
            raise ValidationError("Guard can only mark arrival from EN_ROUTE state.")
        booking.guard_arrive()
        booking.save()
        return booking

    @staticmethod
    def checkin(
        booking: Booking, guard_user: UserProfile, latitude, longitude, notes=""
    ) -> GuardCheckIn:
        if not booking.guard or booking.guard.user != guard_user:
            raise PermissionDenied("Only the assigned guard can check in.")
        if booking.status != "ACTIVE":
            raise ValidationError("Check-in only allowed during active session.")
        checkin = GuardCheckIn.objects.create(
            booking=booking,
            guard=booking.guard,
            latitude=latitude,
            longitude=longitude,
            notes=notes,
        )
        return checkin

    @staticmethod
    def dispute_booking(
        booking: Booking, user: UserProfile, reason: str = ""
    ) -> Booking:
        is_participant = booking.user == user or (
            booking.guard and booking.guard.user == user
        )
        if not is_participant:
            raise PermissionDenied("Only booking participants can raise a dispute.")
        if booking.status != "ACTIVE":
            raise ValidationError("Disputes can only be raised on active sessions.")
        booking.dispute_session()
        booking.admin_notes = f"Dispute raised by {user}: {reason}"
        booking.save()
        return booking

    @staticmethod
    def get_active_booking(user: UserProfile):
        return (
            Booking.objects.filter(
                user=user,
                status__in=[
                    "REQUESTED",
                    "BROADCAST",
                    "ACCEPTED",
                    "EN_ROUTE",
                    "ARRIVED",
                    "ACTIVE",
                ],
            )
            .order_by("-created_at")
            .first()
        )
