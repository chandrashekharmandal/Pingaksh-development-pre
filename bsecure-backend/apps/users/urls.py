from django.urls import path
from . import views
from apps.notifications.views import NotificationPreferenceView

app_name = "users"

urlpatterns = [
    path("me/", views.MeView.as_view(), name="me"),
    path("me/photo/", views.MePhotoView.as_view(), name="me-photo"),
    path("me/addresses/", views.AddressListCreateView.as_view(), name="address-list"),
    path(
        "me/addresses/<uuid:pk>/",
        views.AddressDetailView.as_view(),
        name="address-detail",
    ),
    path(
        "me/emergency-contacts/",
        views.EmergencyContactListCreateView.as_view(),
        name="emergency-contact-list",
    ),
    path(
        "me/emergency-contacts/<uuid:pk>/",
        views.EmergencyContactDetailView.as_view(),
        name="emergency-contact-detail",
    ),
    path(
        "me/bookings/", views.UserBookingHistoryView.as_view(), name="booking-history"
    ),
    path("me/wallet/", views.UserWalletView.as_view(), name="wallet"),
    path("me/fcm-token/", views.FCMTokenView.as_view(), name="fcm-token"),
    path("me/account/", views.AccountDeletionView.as_view(), name="account-delete"),
    path(
        "me/notification-preferences/",
        NotificationPreferenceView.as_view(),
        name="notification-preferences",
    ),
]
