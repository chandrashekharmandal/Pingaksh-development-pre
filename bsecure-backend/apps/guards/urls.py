from django.urls import path
from . import views

app_name = "guards"

urlpatterns = [
    path("me/", views.GuardMeView.as_view(), name="guard-me"),
    path(
        "me/online-status/",
        views.GuardOnlineStatusView.as_view(),
        name="guard-online-status",
    ),
    path("me/documents/", views.GuardDocumentView.as_view(), name="guard-documents"),
    path(
        "me/availability/",
        views.GuardAvailabilityView.as_view(),
        name="guard-availability",
    ),
    path("me/earnings/", views.GuardEarningsView.as_view(), name="guard-earnings"),
    path(
        "me/booking-requests/",
        views.GuardBookingRequestsView.as_view(),
        name="guard-booking-requests",
    ),
    path("nearby/", views.GuardNearbyView.as_view(), name="guard-nearby"),
    path(
        "<uuid:pk>/",
        views.GuardPublicProfileView.as_view(),
        name="guard-public-profile",
    ),
    path(
        "<uuid:pk>/reviews/",
        views.GuardPublicReviewsView.as_view(),
        name="guard-public-reviews",
    ),
]
