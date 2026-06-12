from django.urls import path
from . import views

app_name = "sos"

urlpatterns = [
    path("trigger/", views.SOSTriggerView.as_view(), name="sos-trigger"),
    path("alerts/", views.SOSAlertListView.as_view(), name="sos-alert-list"),
    path(
        "alerts/<uuid:pk>/", views.SOSAlertDetailView.as_view(), name="sos-alert-detail"
    ),
]
