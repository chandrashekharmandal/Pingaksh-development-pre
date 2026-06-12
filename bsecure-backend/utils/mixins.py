from rest_framework import mixins, viewsets, status
from rest_framework.response import Response


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet with create, list, and retrieve only (no update/delete)."""

    pass


class ReadOnlyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet with list and retrieve only."""

    pass


class StandardResponseMixin:
    """
    Mixin to wrap single-object responses in the standard envelope:
    {"data": {...}, "message": "..."}
    """

    def get_success_response(self, data, message: str = "", status_code: int = 200):
        response_data = {"data": data}
        if message:
            response_data["message"] = message
        return Response(response_data, status=status_code)

    def get_created_response(self, data, message: str = "Created successfully."):
        return self.get_success_response(data, message, status.HTTP_201_CREATED)
