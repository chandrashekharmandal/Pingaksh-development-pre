import django.utils.timezone as tz
from apps.guards.models import GuardProfile, GuardDocument, GuardAvailability
from apps.users.models import UserProfile
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


class GuardService:
    @staticmethod
    def get_guard_profile(user: UserProfile) -> GuardProfile:
        try:
            return user.guard_profile
        except GuardProfile.DoesNotExist:
            raise NotFound("Guard profile not found.")

    @staticmethod
    def update_guard_profile(guard: GuardProfile, validated_data: dict) -> GuardProfile:
        for attr, value in validated_data.items():
            setattr(guard, attr, value)
        guard.save()
        return guard

    @staticmethod
    def set_online_status(
        guard: GuardProfile, is_online: bool, latitude=None, longitude=None
    ) -> GuardProfile:
        if is_online and guard.verification_status != "ACTIVE":
            raise PermissionDenied("Only verified (ACTIVE) guards can go online.")
        guard.is_online = is_online
        if is_online and latitude is not None and longitude is not None:
            guard.last_location_update = tz.now()
        if not is_online:
            guard.last_location_update = None
        guard.save(update_fields=["is_online", "last_location_update"])
        return guard

    @staticmethod
    def upload_document(
        guard: GuardProfile, document_type: str, file, expiry_date=None
    ) -> GuardDocument:
        doc, created = GuardDocument.objects.update_or_create(
            guard=guard,
            document_type=document_type,
            defaults={
                "file": file,
                "file_name": file.name,
                "expiry_date": expiry_date,
                "status": "UPLOADED",
            },
        )
        return doc

    @staticmethod
    def list_documents(guard: GuardProfile):
        return GuardDocument.objects.filter(guard=guard).order_by("document_type")

    @staticmethod
    def get_availability(guard: GuardProfile):
        return GuardAvailability.objects.filter(guard=guard).order_by("weekday")

    @staticmethod
    def update_availability(guard: GuardProfile, slots: list) -> list:
        """
        Replace guard's full availability schedule.
        `slots` is a list of dicts with weekday, start_time, end_time, is_available.
        """
        GuardAvailability.objects.filter(guard=guard).delete()
        created = []
        for slot in slots:
            obj = GuardAvailability.objects.create(guard=guard, **slot)
            created.append(obj)
        return created

    @staticmethod
    def get_earnings(
        guard: GuardProfile, period: str = "this_week", from_date=None, to_date=None
    ):
        from apps.bookings.models import Booking
        from django.db.models import Sum, Count
        import datetime

        today = tz.now().date()
        if period == "this_week":
            start = today - datetime.timedelta(days=today.weekday())
            end = today
        elif period == "this_month":
            start = today.replace(day=1)
            end = today
        elif period == "last_month":
            first_this = today.replace(day=1)
            end = first_this - datetime.timedelta(days=1)
            start = end.replace(day=1)
        elif period == "custom" and from_date and to_date:
            start = from_date
            end = to_date
        else:
            start = today - datetime.timedelta(days=7)
            end = today

        bookings = Booking.objects.filter(
            guard=guard,
            state="COMPLETED",
            scheduled_start__date__gte=start,
            scheduled_start__date__lte=end,
        )
        agg = bookings.aggregate(
            total_earnings=Sum("guard_earnings"),
            total_sessions=Count("id"),
        )
        breakdown = []
        for b in bookings.order_by("-scheduled_start"):
            breakdown.append(
                {
                    "booking_id": str(b.id),
                    "date": b.scheduled_start.date().isoformat(),
                    "duration_hours": b.duration_hours,
                    "earnings": str(b.guard_earnings or "0.00"),
                    "service_type": b.service_type,
                }
            )

        return {
            "period": period,
            "total_earnings": str(agg["total_earnings"] or "0.00"),
            "total_sessions": agg["total_sessions"] or 0,
            "total_hours": sum(b.duration_hours for b in bookings),
            "breakdown": breakdown,
        }
