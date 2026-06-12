from rest_framework import serializers
from .models import UserProfile, Address, EmergencyContact


class UserProfileSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "phone_number",
            "full_name",
            "email",
            "gender",
            "date_of_birth",
            "profile_photo_url",
            "role",
            "is_suspended",
            "wallet_balance",
            "total_bookings",
            "created_at",
        ]
        read_only_fields = ["id", "phone_number", "role", "is_suspended", "created_at"]

    def get_wallet_balance(self, obj):
        try:
            return str(obj.wallet.balance)
        except Exception:
            return "0.00"

    def get_total_bookings(self, obj):
        return obj.bookings.count()

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["full_name", "email", "gender", "date_of_birth"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "custom_label",
            "line1",
            "line2",
            "city",
            "state",
            "pincode",
            "country",
            "latitude",
            "longitude",
            "is_default",
        ]
        read_only_fields = ["id"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "name",
            "phone_number",
            "relationship",
            "is_primary",
            "is_verified",
        ]
        read_only_fields = ["id", "is_verified"]


class FCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=512)
