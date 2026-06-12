from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from utils.permissions import IsVerifiedUser
from .models import Review
from .serializers import ReviewSerializer


class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        from apps.bookings.models import Booking
        from apps.guards.models import GuardProfile

        booking_id = request.data.get("booking_id")
        if not booking_id:
            return Response(
                {
                    "error": {
                        "code": "MISSING_BOOKING",
                        "message": "booking_id is required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Booking not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if booking.status != "COMPLETED":
            return Response(
                {
                    "error": {
                        "code": "INVALID_STATE",
                        "message": "Can only review completed bookings.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Review.objects.filter(booking=booking).exists():
            return Response(
                {
                    "error": {
                        "code": "DUPLICATE_REVIEW",
                        "message": "You have already reviewed this booking.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(
            booking=booking,
            reviewer=request.user,
            guard=booking.guard,
            **{k: v for k, v in serializer.validated_data.items()},
        )
        return Response(
            {"data": ReviewSerializer(review).data},
            status=status.HTTP_201_CREATED,
        )


class ReviewFlagView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        try:
            review = Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Review not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        reason = request.data.get("reason", "")
        review.is_flagged = True
        review.flag_reason = reason
        review.save(update_fields=["is_flagged", "flag_reason"])
        return Response({"data": {"message": "Review flagged for moderation."}})
