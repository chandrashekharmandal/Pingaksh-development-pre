from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wrap all DRF errors in the standard b-secure error envelope:

    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {}
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "error": {
                "code": _get_error_code(response.status_code),
                "message": _flatten_errors(response.data),
                "details": response.data if isinstance(response.data, dict) else {},
            }
        }
        response.data = error_data
    else:
        # Unhandled exception — 500
        logger.exception("Unhandled exception in view", exc_info=exc)
        response = Response(
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_error_code(status_code: int) -> str:
    codes = {
        400: "VALIDATION_ERROR",
        401: "AUTHENTICATION_REQUIRED",
        403: "PERMISSION_DENIED",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    return codes.get(status_code, "ERROR")


def _flatten_errors(data) -> str:
    """Extract a single human-readable error message from DRF error data."""
    if isinstance(data, dict):
        # Skip the 'detail' key first (standard DRF)
        if "detail" in data:
            return str(data["detail"])
        for key, value in data.items():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
    elif isinstance(data, list) and data:
        return str(data[0])
    return str(data)


class ServiceException(Exception):
    """Base exception for all service-layer errors."""

    default_code = "SERVICE_ERROR"
    default_message = "A service error occurred."
    status_code = 400

    def __init__(self, message: str = None, code: str = None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)


class InsufficientBalanceError(ServiceException):
    default_code = "INSUFFICIENT_BALANCE"
    default_message = "Insufficient wallet balance."


class NoGuardsAvailableError(ServiceException):
    default_code = "NO_GUARDS_AVAILABLE"
    default_message = "No guards available in your area right now."
    status_code = 404


class InvalidStateTransitionError(ServiceException):
    default_code = "INVALID_STATE"
    default_message = "This action is not allowed in the current state."


class OTPExpiredError(ServiceException):
    default_code = "OTP_EXPIRED"
    default_message = "The OTP has expired. Please request a new one."


class OTPInvalidError(ServiceException):
    default_code = "OTP_INVALID"
    default_message = "The OTP is incorrect."


class OTPLockedError(ServiceException):
    default_code = "OTP_LOCKED"
    default_message = "Too many failed attempts. Please request a new OTP."
    status_code = 429
