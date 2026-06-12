from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsVerifiedUser
from utils.pagination import StandardResultsPagination
from .serializers import (
    WalletSerializer,
    TransactionSerializer,
    TopupInitiateSerializer,
    TopupConfirmSerializer,
)
from .services import PaymentService


class WalletView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        wallet = PaymentService.get_wallet(request.user)
        txns = PaymentService.get_transactions(request.user)[:10]
        return Response(
            {
                "data": {
                    "wallet": WalletSerializer(wallet).data,
                    "recent_transactions": TransactionSerializer(txns, many=True).data,
                }
            }
        )


class TopupInitiateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        serializer = TopupInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = PaymentService.initiate_topup(
            request.user,
            amount=serializer.validated_data["amount"],
            gateway=serializer.validated_data["gateway"],
        )
        return Response({"data": result})


class TopupConfirmView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        serializer = TopupConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        result = PaymentService.confirm_topup(
            request.user,
            gateway_order_id=d["gateway_order_id"],
            gateway_payment_id=d["gateway_payment_id"],
            gateway_signature=d["gateway_signature"],
        )
        return Response({"data": result})


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        txns = PaymentService.get_transactions(request.user)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(txns, request)
        return paginator.get_paginated_response(
            {"data": TransactionSerializer(page, many=True).data}
        )


class RazorpayWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        signature = request.META.get("HTTP_X_RAZORPAY_SIGNATURE", "")
        try:
            result = PaymentService.handle_razorpay_webhook(request.body, signature)
            return Response(result)
        except Exception:
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)
