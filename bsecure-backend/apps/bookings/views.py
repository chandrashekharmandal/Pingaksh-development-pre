from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsVerifiedUser
from .serializers import BookingSerializer, BookingCreateSerializer
from .services import BookingService
from .models import Booking, GuardCheckIn


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        from utils.exceptions import InsufficientBalanceError, NoGuardsAvailableError

        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            booking = BookingService.create_booking(
                request.user, serializer.validated_data
            )
        except InsufficientBalanceError as e:
            return Response(
                {"error": {"code": "INSUFFICIENT_BALANCE", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except NoGuardsAvailableError as e:
            return Response(
                {"error": {"code": "NO_GUARDS_AVAILABLE", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"data": BookingSerializer(booking).data},
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        return Response({"data": BookingSerializer(booking).data})


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        reason = request.data.get("reason", "")
        booking = BookingService.cancel_booking(booking, request.user, reason)
        return Response({"data": BookingSerializer(booking).data})


class GenerateStartOTPView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        otp = BookingService.generate_start_otp(booking, request.user)
        return Response(
            {
                "data": {
                    "otp": otp,
                    "message": "Share this OTP with the guard to start your session.",
                }
            }
        )


class VerifyStartOTPView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        otp = request.data.get("otp")
        if not otp:
            return Response(
                {"error": {"code": "MISSING_OTP", "message": "OTP is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking = BookingService.verify_start_otp(booking, request.user, str(otp))
        return Response({"data": BookingSerializer(booking).data})


class GenerateEndOTPView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        otp = BookingService.generate_end_otp(booking, request.user)
        return Response(
            {
                "data": {
                    "otp": otp,
                    "message": "Share this OTP with the guard to end your session.",
                }
            }
        )


class VerifyEndOTPView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        otp = request.data.get("otp")
        if not otp:
            return Response(
                {"error": {"code": "MISSING_OTP", "message": "OTP is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking = BookingService.verify_end_otp(booking, request.user, str(otp))
        return Response({"data": BookingSerializer(booking).data})


class GuardEnRouteView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        booking = BookingService.guard_en_route(booking, request.user)
        return Response({"data": BookingSerializer(booking).data})


class GuardArrivedView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        booking = BookingService.guard_arrived(booking, request.user)
        return Response({"data": BookingSerializer(booking).data})


class GuardCheckinView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        notes = request.data.get("notes", "")
        if latitude is None or longitude is None:
            return Response(
                {
                    "error": {
                        "code": "MISSING_LOCATION",
                        "message": "latitude and longitude are required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        checkin = BookingService.checkin(
            booking, request.user, latitude, longitude, notes
        )
        return Response(
            {
                "data": {
                    "id": str(checkin.id),
                    "created_at": checkin.created_at.isoformat(),
                }
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        checkins = GuardCheckIn.objects.filter(booking=booking).order_by("-created_at")
        data = [
            {
                "id": str(c.id),
                "latitude": str(c.latitude),
                "longitude": str(c.longitude),
                "notes": c.notes,
                "created_at": c.created_at.isoformat(),
            }
            for c in checkins
        ]
        return Response({"data": data})


class ActiveBookingView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        booking = BookingService.get_active_booking(request.user)
        if not booking:
            return Response({"data": None})
        return Response({"data": BookingSerializer(booking).data})


class BookingDisputeView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, pk):
        booking = BookingService.get_booking(pk, request.user)
        reason = request.data.get("reason", "")
        booking = BookingService.dispute_booking(booking, request.user, reason)
        return Response({"data": BookingSerializer(booking).data})
