from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    # Django admin (internal)
    path("django-admin/", admin.site.urls),
    # API schema & docs (disable or protect in production)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Health check
    path("api/health/", include("apps.core.urls")),
    # Authentication
    path("api/auth/", include("apps.authentication.urls")),
    # User-facing APIs
    path("api/users/", include("apps.users.urls")),
    path("api/guards/", include("apps.guards.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/tracking/", include("apps.tracking.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/sos/", include("apps.sos.urls")),
    path("api/incidents/", include("apps.sos.incident_urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    # Admin panel APIs (IsAdminUser only)
    path("api/admin/", include("apps.admin_panel.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
