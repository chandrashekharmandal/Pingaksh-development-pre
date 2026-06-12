from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Address, EmergencyContact


@admin.register(UserProfile)
class UserProfileAdmin(BaseUserAdmin):
    list_display = (
        "phone_number",
        "full_name",
        "role",
        "is_active",
        "is_suspended",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_suspended", "is_deleted")
    search_fields = ("phone_number", "full_name", "email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "full_name",
                    "email",
                    "gender",
                    "date_of_birth",
                    "profile_photo",
                )
            },
        ),
        (
            "Role & Status",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_suspended",
                    "suspension_reason",
                    "is_deleted",
                )
            },
        ),
        (
            "Auth",
            {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "city", "state", "is_default")
    list_filter = ("label", "city", "state")
    search_fields = ("user__phone_number", "line1", "city")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "phone_number", "relationship", "is_primary")
    search_fields = ("user__phone_number", "name", "phone_number")
