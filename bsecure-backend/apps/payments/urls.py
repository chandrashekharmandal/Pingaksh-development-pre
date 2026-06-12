from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("wallet/", views.WalletView.as_view(), name="wallet"),
    path(
        "wallet/topup/initiate/",
        views.TopupInitiateView.as_view(),
        name="topup-initiate",
    ),
    path(
        "wallet/topup/confirm/", views.TopupConfirmView.as_view(), name="topup-confirm"
    ),
    path("transactions/", views.TransactionListView.as_view(), name="transactions"),
    path(
        "webhook/razorpay/",
        views.RazorpayWebhookView.as_view(),
        name="razorpay-webhook",
    ),
]
