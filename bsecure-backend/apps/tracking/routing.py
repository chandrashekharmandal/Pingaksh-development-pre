from django.urls import re_path
from .consumers import TrackingConsumer

tracking_websocket_urlpatterns = [
    re_path(
        r"^ws/tracking/(?P<booking_id>[0-9a-f-]{36})/$",
        TrackingConsumer.as_asgi(),
    ),
]
