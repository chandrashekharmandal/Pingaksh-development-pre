from rest_framework import throttling


class OTPRequestThrottle(throttling.SimpleRateThrottle):
    """
    Rate limit OTP send requests: max 5 per phone number per 10 minutes.
    Uses the phone_number from the request body as the cache key.
    """

    scope = "otp_request"
    THROTTLE_RATES = {"otp_request": "5/m"}

    def get_cache_key(self, request, view):
        phone_number = request.data.get("phone_number", "")
        if not phone_number:
            return None
        ident = phone_number.strip().replace("+", "").replace(" ", "")
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class OTPVerifyThrottle(throttling.SimpleRateThrottle):
    """
    Rate limit OTP verification attempts: max 10 per IP per 10 minutes.
    Prevents brute-force attacks on OTP codes.
    """

    scope = "otp_verify"
    THROTTLE_RATES = {"otp_verify": "10/m"}

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
