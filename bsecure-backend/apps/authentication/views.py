import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.serializers import (
    AppleSocialAuthSerializer,
    GoogleSocialAuthSerializer,
    LogoutSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
)
from apps.authentication.services import OTPService
from apps.authentication.throttles import OTPRequestThrottle, OTPVerifyThrottle
from utils.exceptions import OTPExpiredError, OTPInvalidError, OTPLockedError
from utils.helpers import get_client_ip

logger = logging.getLogger(__name__)
User = get_user_model()


def _get_tokens_for_user(user) -> dict:
    """Generate JWT access + refresh token pair for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class SendOTPView(APIView):
    """
    POST /api/auth/send-otp/
    Send a 6-digit OTP to the given phone number.
    Rate-limited: max 5 requests per phone per 10 minutes.
    """

    permission_classes = [AllowAny]
    throttle_classes = [OTPRequestThrottle]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        role = serializer.validated_data["role"]
        ip = get_client_ip(request)

        OTPService.send_otp(phone_number, role=role, ip_address=ip)

        return Response(
            {
                "data": {
                    "message": "OTP sent successfully.",
                    "expires_in": settings.OTP_EXPIRY_SECONDS,
                }
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/
    Verify OTP and return JWT tokens. Creates the user account if first login.
    """

    permission_classes = [AllowAny]
    throttle_classes = [OTPVerifyThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_code = serializer.validated_data["otp_code"]
        role = serializer.validated_data["role"]

        try:
            user, is_new_user = OTPService.verify_otp(phone_number, otp_code, role)
        except OTPLockedError as e:
            return Response(
                {"error": {"code": e.code, "message": e.message, "details": {}}},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except (OTPExpiredError, OTPInvalidError) as e:
            return Response(
                {"error": {"code": e.code, "message": e.message, "details": {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = _get_tokens_for_user(user)

        return Response(
            {
                "data": {
                    **tokens,
                    "is_new_user": is_new_user,
                    "role": user.role,
                    "user_id": str(user.id),
                }
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklist the refresh token so it cannot be used again.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            return Response(
                {
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid or expired refresh token.",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"data": {"message": "Logged out successfully."}},
            status=status.HTTP_200_OK,
        )


class GoogleSocialAuthView(APIView):
    """
    POST /api/auth/social/google/
    Authenticate with a Google ID token obtained from client-side Google Sign-In.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token = serializer.validated_data["id_token"]
        role = serializer.validated_data["role"]

        try:
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests

            idinfo = google_id_token.verify_oauth2_token(
                id_token,
                google_requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            )

            google_id = idinfo["sub"]
            email = idinfo.get("email", "")
            full_name = idinfo.get("name", "")

        except Exception as e:
            logger.warning(f"Google token verification failed: {e}")
            return Response(
                {
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid Google token.",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(
            google_id=google_id,
            defaults={
                "email": email,
                "full_name": full_name,
                "role": role,
                "is_active": True,
                # Phone number is required — prompt user to add it after social login
                "phone_number": f"google_{google_id}",
            },
        )

        # Update profile info from Google if not already set
        if not created and not user.full_name:
            user.full_name = full_name
            user.save(update_fields=["full_name"])

        tokens = _get_tokens_for_user(user)
        return Response(
            {
                "data": {
                    **tokens,
                    "is_new_user": created,
                    "role": user.role,
                    "user_id": str(user.id),
                    "needs_phone_verification": user.phone_number.startswith("google_"),
                }
            }
        )


class AppleSocialAuthView(APIView):
    """
    POST /api/auth/social/apple/
    Authenticate with an Apple identity token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AppleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identity_token = serializer.validated_data["identity_token"]
        role = serializer.validated_data["role"]
        full_name = serializer.validated_data.get("full_name", "")

        try:
            import jwt as pyjwt

            # Decode without verification first to get the kid
            header = pyjwt.get_unverified_header(identity_token)
            # Full Apple JWT verification requires fetching Apple's public keys
            # Simplified here — in production use python-social-auth or apple-auth library
            payload = pyjwt.decode(
                identity_token,
                options={"verify_signature": False},  # Replace with proper verification
            )
            apple_id = payload["sub"]
            email = payload.get("email", "")

        except Exception as e:
            logger.warning(f"Apple token verification failed: {e}")
            return Response(
                {
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid Apple identity token.",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(
            apple_id=apple_id,
            defaults={
                "email": email,
                "full_name": full_name,
                "role": role,
                "is_active": True,
                "phone_number": f"apple_{apple_id}",
            },
        )

        tokens = _get_tokens_for_user(user)
        return Response(
            {
                "data": {
                    **tokens,
                    "is_new_user": created,
                    "role": user.role,
                    "user_id": str(user.id),
                    "needs_phone_verification": user.phone_number.startswith("apple_"),
                }
            }
        )
