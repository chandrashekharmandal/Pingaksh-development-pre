from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsVerifiedUser
from utils.pagination import StandardResultsPagination
from .models import NotificationLog, NotificationPreference
from .serializers import NotificationLogSerializer, NotificationPreferenceSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        notifs = NotificationLog.objects.filter(
            recipient=request.user, channel="IN_APP"
        ).order_by("-created_at")
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(notifs, request)
        return paginator.get_paginated_response(
            {"data": NotificationLogSerializer(page, many=True).data}
        )


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        from django.utils import timezone

        try:
            notif = NotificationLog.objects.get(id=pk, recipient=request.user)
        except NotificationLog.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Notification not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=["is_read", "read_at"])
        return Response({"data": {"message": "Notification marked as read."}})


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        from django.utils import timezone

        NotificationLog.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"data": {"message": "All notifications marked as read."}})


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        count = NotificationLog.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"data": {"unread_count": count}})


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        return Response({"data": NotificationPreferenceSerializer(prefs).data})

    def put(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(
            prefs, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": serializer.data})
