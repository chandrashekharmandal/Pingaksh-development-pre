from django.urls import re_path
from .consumers import AdminDashboardConsumer

admin_websocket_urlpatterns = [
    re_path(r"^ws/admin/dashboard/$", AdminDashboardConsumer.as_asgi()),
]
