import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from utils.ws_middleware import JWTAuthMiddlewareStack  # noqa: E402
from apps.tracking.routing import tracking_websocket_urlpatterns  # noqa: E402
from apps.sos.routing import sos_websocket_urlpatterns  # noqa: E402
from apps.admin_panel.routing import admin_websocket_urlpatterns  # noqa: E402

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(
                URLRouter(
                    tracking_websocket_urlpatterns
                    + sos_websocket_urlpatterns
                    + admin_websocket_urlpatterns
                )
            )
        ),
    }
)
