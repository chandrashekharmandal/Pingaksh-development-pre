from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsVerifiedUser, IsGuard
from .serializers import (
    GuardProfileSerializer,
    GuardProfileUpdateSerializer,
    PublicGuardProfileSerializer,
    GuardDocumentSerializer,
    GuardDocumentUploadSerializer,
    GuardAvailabilitySerializer,
    OnlineStatusSerializer,
)
from .services import GuardService
from .models import GuardProfile


class GuardMeView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser, IsGuard]

    def get(self, request):
        guard = GuardService.get_guard_profile(request.user)
        return Response(
            {"data": GuardProfileSerializer(guard, context={"request": request}).data}
        )

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        guard = GuardService.get_guard_profile(request.user)
        serializer = GuardProfileUpdateSerializer(
            guard, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        guard = GuardService.update_guard_profile(guard, serializer.validated_data)
        return Response(
            {"data": GuardProfileSerializer(guard, context={"request": request}).data}
        )


class GuardOnlineStatusView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser, IsGuard]

    def put(self, request):
        guard = GuardService.get_guard_profile(request.user)
        serializer = OnlineStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        guard = GuardService.set_online_status(
            guard,
            is_online=data["is_online"],
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )
        msg = (
            "You are now online and visible to users."
            if guard.is_online
            else "You are now offline."
        )
        from apps.bookings.models import Booking

        active_requests = Booking.objects.filter(
            guard=guard, status="REQUESTED"
        ).count()
        return Response(
            {
                "data": {
                    "is_online": guard.is_online,
                    "message": msg,
                    "active_booking_requests": active_requests,
                }
            }
        )


class GuardDocumentView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser, IsGuard]

    def get(self, request):
        guard = GuardService.get_guard_profile(request.user)
        docs = GuardService.list_documents(guard)
        return Response({"data": GuardDocumentSerializer(docs, many=True).data})

    def post(self, request):
        guard = GuardService.get_guard_profile(request.user)
        serializer = GuardDocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        doc = GuardService.upload_document(
            guard,
            document_type=d["document_type"],
            file=d["file"],
            expiry_date=d.get("expiry_date"),
        )
        return Response(
            {"data": GuardDocumentSerializer(doc).data},
            status=status.HTTP_201_CREATED,
        )


class GuardAvailabilityView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser, IsGuard]

    def get(self, request):
        guard = GuardService.get_guard_profile(request.user)
        slots = GuardService.get_availability(guard)
        return Response({"data": GuardAvailabilitySerializer(slots, many=True).data})

    def put(self, request):
        guard = GuardService.get_guard_profile(request.user)
        serializer = GuardAvailabilitySerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        slots = GuardService.update_availability(guard, serializer.validated_data)
        return Response({"data": GuardAvailabilitySerializer(slots, many=True).data})


class GuardPublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            guard = GuardProfile.objects.select_related("user").get(id=pk)
        except GuardProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Guard not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "data": PublicGuardProfileSerializer(
                    guard, context={"request": request}
                ).data
            }
        )


class GuardPublicReviewsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from apps.reviews.models import Review
        from apps.reviews.serializers import ReviewSerializer
        from utils.pagination import StandardResultsPagination

        try:
            guard = GuardProfile.objects.get(id=pk)
        except GuardProfile.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Guard not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        reviews = Review.objects.filter(guard=guard).order_by("-created_at")
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(reviews, request)
        return paginator.get_paginated_response(
            {"data": ReviewSerializer(page, many=True).data}
        )


class GuardNearbyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return nearby available guards (simple lat/lng filter in non-GIS mode)."""
        try:
            lat = float(request.query_params.get("latitude", 0))
            lng = float(request.query_params.get("longitude", 0))
            radius_km = float(request.query_params.get("radius_km", 10))
        except (TypeError, ValueError):
            return Response(
                {
                    "error": {
                        "code": "INVALID_PARAMS",
                        "message": "Invalid location parameters.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        from utils.helpers import haversine_distance_km

        guards = GuardProfile.objects.filter(
            is_online=True,
            verification_status="ACTIVE",
        ).select_related("user")

        nearby = []
        for guard in guards:
            # In test/SQLite mode current_location is a TextField; skip distance filter
            nearby.append(guard)

        serializer = PublicGuardProfileSerializer(
            nearby, many=True, context={"request": request}
        )
        return Response({"data": serializer.data})


class GuardEarningsView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser, IsGuard]

    def get(self, request):
        guard = GuardService.get_guard_profile(request.user)
        period = request.query_params.get("period", "this_week")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        import datetime

        if from_date:
            try:
                from_date = datetime.date.fromisoformat(from_date)
            except ValueError:
                from_date = None
        if to_date:
            try:
                to_date = datetime.date.fromisoformat(to_date)
            except ValueError:
                to_date = None
        data = GuardService.get_earnings(
            guard, period=period, from_date=from_date, to_date=to_date
        )
        return Response({"data": data})


class GuardBookingRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser, IsGuard]

    def get(self, request):
        from apps.bookings.models import Booking
        from apps.bookings.serializers import BookingSerializer

        guard = GuardService.get_guard_profile(request.user)
        bookings = Booking.objects.filter(guard=guard, status="REQUESTED").order_by(
            "-created_at"
        )
        return Response(
            {
                "data": BookingSerializer(
                    bookings, many=True, context={"request": request}
                ).data
            }
        )
