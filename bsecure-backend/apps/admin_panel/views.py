from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from utils.permissions import IsAdminUser
from utils.pagination import StandardResultsPagination


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        from apps.bookings.models import Booking
        from apps.guards.models import GuardProfile
        from apps.users.models import UserProfile
        from apps.sos.models import SOSAlert
        from django.db.models import Sum
        import datetime

        today = timezone.now().date()

        realtime = {
            "active_sessions": Booking.objects.filter(status="ACTIVE").count(),
            "guards_online": GuardProfile.objects.filter(is_online=True).count(),
            "users_in_app": UserProfile.objects.filter(
                is_active=True, role="USER"
            ).count(),
            "open_sos_alerts": SOSAlert.objects.filter(status="TRIGGERED").count(),
            "pending_guard_approvals": GuardProfile.objects.filter(
                verification_status="UNDER_REVIEW"
            ).count(),
        }

        today_bookings = Booking.objects.filter(created_at__date=today)
        today_data = {
            "total_bookings": today_bookings.count(),
            "completed_bookings": today_bookings.filter(status="COMPLETED").count(),
            "cancelled_bookings": today_bookings.filter(status="CANCELLED").count(),
            "gross_revenue": str(
                today_bookings.filter(status="COMPLETED").aggregate(
                    total=Sum("total_amount")
                )["total"]
                or "0.00"
            ),
            "new_users": UserProfile.objects.filter(
                created_at__date=today, role="USER"
            ).count(),
            "new_guards": UserProfile.objects.filter(
                created_at__date=today, role="GUARD"
            ).count(),
        }

        first_of_month = today.replace(day=1)
        month_bookings = Booking.objects.filter(created_at__date__gte=first_of_month)
        month_data = {
            "total_bookings": month_bookings.count(),
            "gross_revenue": str(
                month_bookings.filter(status="COMPLETED").aggregate(
                    total=Sum("total_amount")
                )["total"]
                or "0.00"
            ),
        }

        return Response(
            {
                "data": {
                    "realtime": realtime,
                    "today": today_data,
                    "this_month": month_data,
                }
            }
        )


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        from apps.users.models import UserProfile
        from apps.users.serializers import UserProfileSerializer

        users = UserProfile.objects.filter(is_deleted=False).order_by("-created_at")
        role = request.query_params.get("role")
        if role:
            users = users.filter(role=role)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(users, request)
        return paginator.get_paginated_response(
            {
                "data": UserProfileSerializer(
                    page, many=True, context={"request": request}
                ).data
            }
        )


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        from apps.users.models import UserProfile
        from apps.users.serializers import UserProfileSerializer

        try:
            user = UserProfile.objects.get(id=pk)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"data": UserProfileSerializer(user, context={"request": request}).data}
        )


class AdminUserSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.users.models import UserProfile

        try:
            user = UserProfile.objects.get(id=pk)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=404,
            )
        user.is_suspended = True
        user.suspension_reason = request.data.get("reason", "Admin suspension")
        user.save(update_fields=["is_suspended", "suspension_reason"])
        return Response({"data": {"message": f"User {user.display_name} suspended."}})


class AdminUserUnsuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.users.models import UserProfile

        try:
            user = UserProfile.objects.get(id=pk)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=404,
            )
        user.is_suspended = False
        user.suspension_reason = ""
        user.save(update_fields=["is_suspended", "suspension_reason"])
        return Response({"data": {"message": f"User {user.display_name} unsuspended."}})


class AdminUserBanView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.users.models import UserProfile

        try:
            user = UserProfile.objects.get(id=pk)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=404,
            )
        user.is_active = False
        user.is_suspended = True
        user.suspension_reason = request.data.get("reason", "Permanently banned")
        user.save(update_fields=["is_active", "is_suspended", "suspension_reason"])
        return Response(
            {"data": {"message": f"User {user.display_name} permanently banned."}}
        )


class AdminUserCreditWalletView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.users.models import UserProfile
        from apps.payments.models import Wallet, Transaction
        import decimal

        try:
            user = UserProfile.objects.get(id=pk)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found."}},
                status=404,
            )
        amount = decimal.Decimal(str(request.data.get("amount", 0)))
        if amount <= 0:
            return Response(
                {
                    "error": {
                        "code": "INVALID_AMOUNT",
                        "message": "Amount must be positive.",
                    }
                },
                status=400,
            )
        wallet, _ = Wallet.objects.get_or_create(user=user)
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.save(update_fields=["balance"])
        Transaction.objects.create(
            wallet=wallet,
            transaction_type="ADMIN_CREDIT",
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            status="SUCCESS",
            description=request.data.get("reason", "Admin wallet credit"),
            admin_note=f"Credited by admin {request.user}",
        )
        return Response({"data": {"new_balance": str(wallet.balance)}})


class AdminGuardListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        from apps.guards.models import GuardProfile
        from apps.guards.serializers import GuardProfileSerializer

        guards = GuardProfile.objects.select_related("user").all()
        vs = request.query_params.get("verification_status")
        if vs:
            guards = guards.filter(verification_status=vs)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(guards, request)
        return paginator.get_paginated_response(
            {
                "data": GuardProfileSerializer(
                    page, many=True, context={"request": request}
                ).data
            }
        )


class AdminGuardApproveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.guards.models import GuardProfile

        try:
            guard = GuardProfile.objects.get(id=pk)
        except GuardProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Guard not found."}},
                status=404,
            )
        guard.verification_status = "ACTIVE"
        guard.verified_at = timezone.now()
        guard.verified_by = request.user
        guard.save(update_fields=["verification_status", "verified_at", "verified_by"])
        return Response({"data": {"message": "Guard approved and activated."}})


class AdminGuardSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.guards.models import GuardProfile

        try:
            guard = GuardProfile.objects.get(id=pk)
        except GuardProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Guard not found."}},
                status=404,
            )
        guard.verification_status = "SUSPENDED"
        guard.is_online = False
        guard.save(update_fields=["verification_status", "is_online"])
        return Response({"data": {"message": "Guard suspended."}})


class AdminDocumentApproveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, guard_pk, doc_pk):
        from apps.guards.models import GuardDocument

        try:
            doc = GuardDocument.objects.get(id=doc_pk, guard_id=guard_pk)
        except GuardDocument.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Document not found."}},
                status=404,
            )
        doc.status = "APPROVED"
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        return Response({"data": {"document_id": str(doc.id), "status": "APPROVED"}})


class AdminDocumentRejectView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, guard_pk, doc_pk):
        from apps.guards.models import GuardDocument

        try:
            doc = GuardDocument.objects.get(id=doc_pk, guard_id=guard_pk)
        except GuardDocument.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Document not found."}},
                status=404,
            )
        notes = request.data.get("review_notes", "")
        doc.status = "REJECTED"
        doc.review_notes = notes
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save(update_fields=["status", "review_notes", "reviewed_by", "reviewed_at"])
        return Response(
            {
                "data": {
                    "document_id": str(doc.id),
                    "status": "REJECTED",
                    "review_notes": notes,
                    "guard_notified": False,
                }
            }
        )


class AdminSOSListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        from apps.sos.models import SOSAlert
        from apps.sos.serializers import SOSAlertSerializer

        alerts = SOSAlert.objects.all()
        s = request.query_params.get("status")
        if s:
            alerts = alerts.filter(status=s)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(alerts, request)
        return paginator.get_paginated_response(
            {"data": SOSAlertSerializer(page, many=True).data}
        )


class AdminSOSAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.sos.models import SOSAlert

        try:
            alert = SOSAlert.objects.get(id=pk)
        except SOSAlert.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "SOS not found."}},
                status=404,
            )
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = timezone.now()
        alert.assigned_to = request.user
        alert.save(update_fields=["status", "acknowledged_at", "assigned_to"])
        return Response({"data": {"message": "SOS acknowledged."}})


class AdminSOSResolveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        from apps.sos.models import SOSAlert

        try:
            alert = SOSAlert.objects.get(id=pk)
        except SOSAlert.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "SOS not found."}},
                status=404,
            )
        alert.status = "RESOLVED"
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get("notes", "")
        alert.save(update_fields=["status", "resolved_at", "resolution_notes"])
        return Response({"data": {"message": "SOS resolved."}})
