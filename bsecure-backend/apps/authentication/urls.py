from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.views import (
    AppleSocialAuthView,
    GoogleSocialAuthView,
    LogoutView,
    SendOTPView,
    VerifyOTPView,
)

app_name = "authentication"

urlpatterns = [
    # OTP
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    # JWT
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Social Auth
    path("social/google/", GoogleSocialAuthView.as_view(), name="google-auth"),
    path("social/apple/", AppleSocialAuthView.as_view(), name="apple-auth"),
]
