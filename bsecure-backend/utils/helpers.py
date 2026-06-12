import random
import string
import hashlib
import secrets
from math import radians, cos, sin, asin, sqrt
from typing import Optional


# ─── OTP ─────────────────────────────────────────────────────────────────────


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of given length."""
    return "".join(random.choices(string.digits, k=length))


def generate_secure_otp(length: int = 6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    return str(secrets.randbelow(10**length)).zfill(length)


def hash_otp(otp: str) -> str:
    """One-way SHA-256 hash of an OTP for safe storage."""
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(raw_otp: str, hashed_otp: str) -> bool:
    """Verify a raw OTP against its stored hash."""
    return hash_otp(raw_otp) == hashed_otp


# ─── Phone ───────────────────────────────────────────────────────────────────


def mask_phone_number(phone: str) -> str:
    """Return a masked phone for display: +91******7890"""
    if len(phone) < 6:
        return phone
    return phone[:3] + "*" * 5 + phone[-4:]


def normalize_phone_number(phone: str) -> str:
    """Ensure phone has + prefix and no spaces."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+91" + phone  # Default to India
    return phone


# ─── Geospatial ──────────────────────────────────────────────────────────────


def haversine_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance in km between two lat/lng points.
    Quick Python check — use PostGIS for production proximity queries.
    """
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


def is_within_radius(
    lat1: float, lng1: float, lat2: float, lng2: float, radius_km: float
) -> bool:
    """Return True if point2 is within radius_km of point1."""
    return haversine_distance_km(lat1, lng1, lat2, lng2) <= radius_km


# ─── Token ───────────────────────────────────────────────────────────────────


def generate_random_token(length: int = 32) -> str:
    """Generate a URL-safe random token."""
    return secrets.token_urlsafe(length)


# ─── Pricing ─────────────────────────────────────────────────────────────────


def calculate_booking_price(
    base_rate_per_hour: float,
    duration_hours: float,
    surge_multiplier: float = 1.0,
    promo_discount: float = 0.0,
    platform_fee_percent: float = 15.0,
    tax_percent: float = 18.0,
) -> dict:
    """
    Calculate full pricing breakdown for a booking.

    Returns:
        {
            'subtotal': float,
            'surge_amount': float,
            'discounted_subtotal': float,
            'platform_fee': float,
            'guard_earnings': float,
            'tax_amount': float,
            'total_amount': float,
        }
    """
    subtotal = base_rate_per_hour * duration_hours
    surge_amount = subtotal * (surge_multiplier - 1.0)
    subtotal_after_surge = subtotal + surge_amount
    discounted_subtotal = max(subtotal_after_surge - promo_discount, 0)
    platform_fee = round(discounted_subtotal * (platform_fee_percent / 100), 2)
    guard_earnings = round(discounted_subtotal - platform_fee, 2)
    tax_amount = round(platform_fee * (tax_percent / 100), 2)
    total_amount = round(discounted_subtotal + tax_amount, 2)

    return {
        "subtotal": round(subtotal, 2),
        "surge_amount": round(surge_amount, 2),
        "discounted_subtotal": round(discounted_subtotal, 2),
        "platform_fee": platform_fee,
        "guard_earnings": guard_earnings,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }


# ─── Misc ─────────────────────────────────────────────────────────────────────


def get_client_ip(request) -> Optional[str]:
    """Extract the real client IP from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
