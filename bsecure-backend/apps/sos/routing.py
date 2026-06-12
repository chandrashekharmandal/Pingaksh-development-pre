from django.urls import re_path
from .consumers import SOSFeedConsumer

sos_websocket_urlpatterns = [
    re_path(r"^ws/sos/feed/$", SOSFeedConsumer.as_asgi()),
]
