from django.contrib import admin
from .models import GuardProfile, GuardDocument, GuardAvailability, GuardBlackoutDate


@admin.register(GuardProfile)
class GuardProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "guard_type",
        "verification_status",
        "is_online",
        "average_rating",
        "total_sessions_completed",
    )
    list_filter = ("guard_type", "verification_status", "is_online")
    search_fields = ("user__phone_number", "user__full_name")
    readonly_fields = ("id", "created_at", "updated_at", "verified_at")


@admin.register(GuardDocument)
class GuardDocumentAdmin(admin.ModelAdmin):
    list_display = ("guard", "document_type", "status", "expiry_date", "reviewed_at")
    list_filter = ("document_type", "status")
    search_fields = ("guard__user__phone_number",)
    readonly_fields = ("id", "created_at", "reviewed_at")


@admin.register(GuardAvailability)
class GuardAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("guard", "weekday", "start_time", "end_time", "is_available")
    list_filter = ("weekday", "is_available")


@admin.register(GuardBlackoutDate)
class GuardBlackoutDateAdmin(admin.ModelAdmin):
    list_display = ("guard", "date", "reason")
    list_filter = ("date",)
