from django.contrib.auth import get_user_model
from rest_framework import serializers

from utils.validators import validate_indian_phone_number

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    role = serializers.ChoiceField(
        choices=["USER", "GUARD", "ADMIN"],
        default="USER",
    )

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        if not value.startswith("+"):
            value = "+91" + value
        validate_indian_phone_number(value)
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(min_length=4, max_length=8)
    role = serializers.ChoiceField(
        choices=["USER", "GUARD", "ADMIN"],
        default="USER",
    )

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        if not value.startswith("+"):
            value = "+91" + value
        validate_indian_phone_number(value)
        return value

    def validate_otp_code(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain digits only.")
        return value


class TokenRefreshSerializer(serializers.Serializer):
    """Thin wrapper — actual logic handled by SimpleJWT view."""

    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class GoogleSocialAuthSerializer(serializers.Serializer):
    """
    Receives a Google ID token from the mobile app
    (obtained after Google Sign-In on client side).
    """

    id_token = serializers.CharField()
    role = serializers.ChoiceField(choices=["USER", "GUARD"], default="USER")


class AppleSocialAuthSerializer(serializers.Serializer):
    """
    Receives Apple identity token from the mobile app.
    """

    identity_token = serializers.CharField()
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=["USER", "GUARD"], default="USER")
