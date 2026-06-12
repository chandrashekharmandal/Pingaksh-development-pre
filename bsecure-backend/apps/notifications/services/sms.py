"""
SMS notification service.
Supports Twilio (default) and MSG91.
To be fully integrated in Phase 5.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    @staticmethod
    def send_otp_sms(phone_number: str, otp: str) -> bool:
        """Send OTP via Twilio."""
        try:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your b-secure OTP is: {otp}. Valid for 5 minutes. Do not share.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number,
            )
            logger.info(f"OTP SMS sent to {phone_number}: SID={message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP SMS to {phone_number}: {e}")
            return False

    @staticmethod
    def send_otp_via_msg91(phone_number: str, otp: str) -> bool:
        """Send OTP via MSG91."""
        import requests as req

        try:
            url = "https://api.msg91.com/api/v5/otp"
            params = {
                "template_id": settings.MSG91_TEMPLATE_ID,
                "mobile": phone_number.lstrip("+"),
                "authkey": settings.MSG91_AUTH_KEY,
                "otp": otp,
            }
            resp = req.post(url, json=params, timeout=10)
            resp.raise_for_status()
            logger.info(f"OTP SMS (MSG91) sent to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"MSG91 OTP failed for {phone_number}: {e}")
            return False

    @staticmethod
    def send_sms(phone_number: str, message: str) -> bool:
        """Send a plain SMS message via Twilio."""
        try:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False
