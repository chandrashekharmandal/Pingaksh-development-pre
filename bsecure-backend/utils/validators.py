import re
from django.core.exceptions import ValidationError


def validate_indian_phone_number(value: str):
    """Validate E.164 format phone number (Indian numbers primarily)."""
    pattern = r"^\+[1-9]\d{7,14}$"
    if not re.match(pattern, value):
        raise ValidationError(
            f"{value} is not a valid phone number. Use E.164 format: +919876543210"
        )


def validate_latitude(value):
    """Validate latitude is within -90 to 90."""
    try:
        lat = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Latitude must be a number.")
    if not (-90 <= lat <= 90):
        raise ValidationError("Latitude must be between -90 and 90.")


def validate_longitude(value):
    """Validate longitude is within -180 to 180."""
    try:
        lng = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Longitude must be a number.")
    if not (-180 <= lng <= 180):
        raise ValidationError("Longitude must be between -180 and 180.")


def validate_image_file(file):
    """Validate uploaded image is within size limits and a supported format."""
    max_size_mb = 10
    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image size must be under {max_size_mb}MB.")

    if hasattr(file, "content_type") and file.content_type not in allowed_types:
        raise ValidationError(
            f"Unsupported image type: {file.content_type}. Allowed: JPEG, PNG, WebP."
        )


def validate_document_file(file):
    """Validate uploaded document (PDF, image)."""
    max_size_mb = 20
    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size must be under {max_size_mb}MB.")

    if hasattr(file, "content_type") and file.content_type not in allowed_types:
        raise ValidationError(f"Unsupported file type. Allowed: PDF, JPEG, PNG, WebP.")


def validate_pincode(value: str):
    """Validate Indian 6-digit PIN code."""
    if not re.match(r"^\d{6}$", str(value)):
        raise ValidationError("PIN code must be a 6-digit number.")
