from django.urls import path
from . import views

urlpatterns = [
    path("", views.IncidentListCreateView.as_view(), name="incident-list-create"),
    path("<uuid:pk>/", views.IncidentDetailView.as_view(), name="incident-detail"),
]
