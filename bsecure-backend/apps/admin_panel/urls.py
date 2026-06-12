from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path(
        "dashboard/stats/",
        views.AdminDashboardStatsView.as_view(),
        name="dashboard-stats",
    ),
    path("users/", views.AdminUserListView.as_view(), name="user-list"),
    path("users/<uuid:pk>/", views.AdminUserDetailView.as_view(), name="user-detail"),
    path(
        "users/<uuid:pk>/suspend/",
        views.AdminUserSuspendView.as_view(),
        name="user-suspend",
    ),
    path(
        "users/<uuid:pk>/unsuspend/",
        views.AdminUserUnsuspendView.as_view(),
        name="user-unsuspend",
    ),
    path("users/<uuid:pk>/ban/", views.AdminUserBanView.as_view(), name="user-ban"),
    path(
        "users/<uuid:pk>/credit-wallet/",
        views.AdminUserCreditWalletView.as_view(),
        name="user-credit-wallet",
    ),
    path("guards/", views.AdminGuardListView.as_view(), name="guard-list"),
    path(
        "guards/<uuid:pk>/approve/",
        views.AdminGuardApproveView.as_view(),
        name="guard-approve",
    ),
    path(
        "guards/<uuid:pk>/suspend/",
        views.AdminGuardSuspendView.as_view(),
        name="guard-suspend",
    ),
    path(
        "guards/<uuid:guard_pk>/documents/<uuid:doc_pk>/approve/",
        views.AdminDocumentApproveView.as_view(),
        name="doc-approve",
    ),
    path(
        "guards/<uuid:guard_pk>/documents/<uuid:doc_pk>/reject/",
        views.AdminDocumentRejectView.as_view(),
        name="doc-reject",
    ),
    path("sos/alerts/", views.AdminSOSListView.as_view(), name="sos-list"),
    path(
        "sos/alerts/<uuid:pk>/acknowledge/",
        views.AdminSOSAcknowledgeView.as_view(),
        name="sos-acknowledge",
    ),
    path(
        "sos/alerts/<uuid:pk>/resolve/",
        views.AdminSOSResolveView.as_view(),
        name="sos-resolve",
    ),
]
