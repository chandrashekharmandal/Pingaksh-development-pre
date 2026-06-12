from rest_framework import serializers
from .models import GuardProfile, GuardDocument, GuardAvailability, GuardBlackoutDate
from apps.users.serializers import UserProfileSerializer


class GuardProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = GuardProfile
        fields = [
            "id",
            "user",
            "guard_type",
            "years_of_experience",
            "bio",
            "languages_spoken",
            "skills",
            "verification_status",
            "is_online",
            "is_available",
            "average_rating",
            "total_reviews",
            "total_sessions_completed",
            "preferred_work_radius_km",
            "max_daily_hours",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "verification_status",
            "average_rating",
            "total_reviews",
            "total_sessions_completed",
            "created_at",
        ]


class GuardProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardProfile
        fields = [
            "guard_type",
            "years_of_experience",
            "bio",
            "languages_spoken",
            "skills",
            "bank_account_number",
            "bank_ifsc_code",
            "upi_id",
            "payout_preference",
            "preferred_work_radius_km",
            "max_daily_hours",
        ]


class PublicGuardProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = GuardProfile
        fields = [
            "id",
            "full_name",
            "profile_photo_url",
            "guard_type",
            "years_of_experience",
            "bio",
            "languages_spoken",
            "skills",
            "average_rating",
            "total_reviews",
            "total_sessions_completed",
            "is_online",
            "is_available",
            "preferred_work_radius_km",
        ]

    def get_profile_photo_url(self, obj):
        if obj.user.profile_photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.user.profile_photo.url)
            return obj.user.profile_photo.url
        return None


class GuardDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )

    class Meta:
        model = GuardDocument
        fields = [
            "id",
            "document_type",
            "document_type_display",
            "file_name",
            "status",
            "expiry_date",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at", "document_type_display"]


class GuardDocumentUploadSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=GuardDocument.DOCUMENT_TYPE_CHOICES)
    file = serializers.FileField()
    expiry_date = serializers.DateField(required=False, allow_null=True)


class GuardAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardAvailability
        fields = ["id", "weekday", "start_time", "end_time", "is_available"]
        read_only_fields = ["id"]


class OnlineStatusSerializer(serializers.Serializer):
    is_online = serializers.BooleanField()
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
