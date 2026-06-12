"""
S3 storage backends and upload path generators for the bSecure platform.

Bucket structure:
  bsecure-{env}/
  ├── media/
  │   ├── guards/{guard_id}/profile/       — profile photos
  │   ├── guards/{guard_id}/documents/     — ID docs, certificates
  │   ├── users/{user_id}/profile/         — user profile photos
  │   └── bookings/{booking_id}/           — booking-related media
  ├── exports/
  │   └── reports/{YYYY-MM}/               — admin export CSVs
  └── static/                              — collectstatic output (public)

Usage in models:
    photo = models.ImageField(upload_to=guard_profile_upload_path)
"""

import uuid
from datetime import datetime

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# ─── Custom Storage Backends ─────────────────────────────────────────────────


class PublicMediaStorage(S3Boto3Storage):
    """For public media (static assets). Files are publicly readable."""

    location = "static"
    default_acl = "public-read"
    file_overwrite = True
    querystring_auth = False


class PrivateMediaStorage(S3Boto3Storage):
    """For private media (user docs, guard docs). Requires pre-signed URLs."""

    location = "media"
    default_acl = "private"
    file_overwrite = False
    querystring_auth = True
    custom_domain = False


class ExportStorage(S3Boto3Storage):
    """For admin export files (reports, CSVs)."""

    location = "exports"
    default_acl = "private"
    file_overwrite = False
    querystring_auth = True


# ─── Upload Path Generators ──────────────────────────────────────────────────


def _unique_filename(filename: str) -> str:
    """Generate a unique filename preserving the extension."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    return f"{uuid.uuid4().hex}.{ext}"


def guard_profile_upload_path(instance, filename: str) -> str:
    """Upload path for guard profile photos."""
    return f"guards/{instance.id}/profile/{_unique_filename(filename)}"


def guard_document_upload_path(instance, filename: str) -> str:
    """Upload path for guard verification documents."""
    guard_id = instance.guard_id if hasattr(instance, "guard_id") else instance.guard.id
    return f"guards/{guard_id}/documents/{_unique_filename(filename)}"


def user_profile_upload_path(instance, filename: str) -> str:
    """Upload path for user profile photos."""
    return f"users/{instance.id}/profile/{_unique_filename(filename)}"


def booking_media_upload_path(instance, filename: str) -> str:
    """Upload path for booking-related media (SOS photos, etc.)."""
    booking_id = instance.booking_id if hasattr(instance, "booking_id") else instance.id
    return f"bookings/{booking_id}/{_unique_filename(filename)}"


def export_report_path(report_type: str) -> str:
    """Generate path for admin export reports."""
    now = datetime.now()
    return f"reports/{now.strftime('%Y-%m')}/{report_type}_{now.strftime('%Y%m%d_%H%M%S')}.csv"
