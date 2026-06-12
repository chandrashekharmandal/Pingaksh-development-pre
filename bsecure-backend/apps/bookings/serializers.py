from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.display_name", read_only=True)
    guard_name = serializers.SerializerMethodField()
    state = serializers.CharField(source="status", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user_name",
            "guard_name",
            "state",
            "service_type",
            "guard_type_requested",
            "service_address",
            "service_latitude",
            "service_longitude",
            "scheduled_start",
            "scheduled_end",
            "base_rate_per_hour",
            "total_amount",
            "platform_fee",
            "guard_earnings",
            "created_at",
        ]
        read_only_fields = fields

    def get_guard_name(self, obj):
        if obj.guard:
            return obj.guard.user.display_name
        return None


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "service_type",
            "guard_type_requested",
            "service_address",
            "service_latitude",
            "service_longitude",
            "scheduled_start",
            "scheduled_end",
            "is_immediate",
            "base_rate_per_hour",
        ]
