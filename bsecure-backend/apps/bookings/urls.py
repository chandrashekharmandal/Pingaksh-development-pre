from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.BookingCreateView.as_view(), name="booking-create"),
    path("active/", views.ActiveBookingView.as_view(), name="booking-active"),
    path("<uuid:pk>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("<uuid:pk>/cancel/", views.BookingCancelView.as_view(), name="booking-cancel"),
    path(
        "<uuid:pk>/generate-start-otp/",
        views.GenerateStartOTPView.as_view(),
        name="booking-generate-start-otp",
    ),
    path(
        "<uuid:pk>/verify-start-otp/",
        views.VerifyStartOTPView.as_view(),
        name="booking-verify-start-otp",
    ),
    path(
        "<uuid:pk>/generate-end-otp/",
        views.GenerateEndOTPView.as_view(),
        name="booking-generate-end-otp",
    ),
    path(
        "<uuid:pk>/verify-end-otp/",
        views.VerifyEndOTPView.as_view(),
        name="booking-verify-end-otp",
    ),
    path(
        "<uuid:pk>/guard-en-route/",
        views.GuardEnRouteView.as_view(),
        name="booking-guard-en-route",
    ),
    path(
        "<uuid:pk>/guard-arrived/",
        views.GuardArrivedView.as_view(),
        name="booking-guard-arrived",
    ),
    path(
        "<uuid:pk>/checkin/", views.GuardCheckinView.as_view(), name="booking-checkin"
    ),
    path(
        "<uuid:pk>/checkins/", views.GuardCheckinView.as_view(), name="booking-checkins"
    ),
    path(
        "<uuid:pk>/dispute/", views.BookingDisputeView.as_view(), name="booking-dispute"
    ),
]
