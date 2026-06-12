from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsVerifiedUser
from .serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    AddressSerializer,
    EmergencyContactSerializer,
    FCMTokenSerializer,
)
from .services import UserService


class MeView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response({"data": serializer.data})

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = UserService.update_profile(request.user, serializer.validated_data)
        return Response(
            {"data": UserProfileSerializer(user, context={"request": request}).data}
        )


class MePhotoView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        photo = request.FILES.get("photo")
        if not photo:
            return Response(
                {"error": {"code": "MISSING_PHOTO", "message": "No photo provided."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.profile_photo = photo
        request.user.save(update_fields=["profile_photo"])
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response({"data": serializer.data})


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        addresses = UserService.list_addresses(request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response({"data": serializer.data})

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = UserService.create_address(request.user, serializer.validated_data)
        return Response(
            {"data": AddressSerializer(address).data},
            status=status.HTTP_201_CREATED,
        )


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def put(self, request, pk):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = UserService.update_address(
            request.user, pk, serializer.validated_data
        )
        return Response({"data": AddressSerializer(address).data})

    def patch(self, request, pk):
        serializer = AddressSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        address = UserService.update_address(
            request.user, pk, serializer.validated_data
        )
        return Response({"data": AddressSerializer(address).data})

    def delete(self, request, pk):
        UserService.delete_address(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmergencyContactListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        contacts = UserService.list_emergency_contacts(request.user)
        serializer = EmergencyContactSerializer(contacts, many=True)
        return Response({"data": serializer.data})

    def post(self, request):
        serializer = EmergencyContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = UserService.create_emergency_contact(
            request.user, serializer.validated_data
        )
        return Response(
            {"data": EmergencyContactSerializer(contact).data},
            status=status.HTTP_201_CREATED,
        )


class EmergencyContactDetailView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def put(self, request, pk):
        serializer = EmergencyContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = UserService.update_emergency_contact(
            request.user, pk, serializer.validated_data
        )
        return Response({"data": EmergencyContactSerializer(contact).data})

    def patch(self, request, pk):
        serializer = EmergencyContactSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        contact = UserService.update_emergency_contact(
            request.user, pk, serializer.validated_data
        )
        return Response({"data": EmergencyContactSerializer(contact).data})

    def delete(self, request, pk):
        UserService.delete_emergency_contact(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FCMTokenView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def put(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.update_fcm_token(
            request.user, serializer.validated_data["fcm_token"]
        )
        return Response({"data": {"message": "FCM token updated."}})


class AccountDeletionView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def delete(self, request):
        UserService.request_account_deletion(request.user)
        return Response(
            {
                "data": {
                    "message": "Account deletion requested. Your account will be removed within 30 days."
                }
            },
            status=status.HTTP_200_OK,
        )


class UserBookingHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        from apps.bookings.models import Booking
        from apps.bookings.serializers import BookingSerializer
        from utils.pagination import StandardResultsPagination

        bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(bookings, request)
        serializer = BookingSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response({"data": serializer.data})


class UserWalletView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        from apps.payments.models import Transaction

        try:
            wallet = request.user.wallet
        except Exception:
            return Response({"data": {"balance": "0.00", "transactions": []}})

        transactions = Transaction.objects.filter(wallet=wallet).order_by(
            "-created_at"
        )[:10]
        from apps.payments.serializers import TransactionSerializer

        return Response(
            {
                "data": {
                    "balance": str(wallet.balance),
                    "transactions": TransactionSerializer(transactions, many=True).data,
                }
            }
        )
