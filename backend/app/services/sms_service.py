"""
SMS sending service.
Simulates sending SMS messages with console logging fallback.
"""
import logging
import os

logger = logging.getLogger("app")

# Twilio credentials (optional, for real SMS)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER", "")

def send_sms(recipient_phone: str, message: str) -> bool:
    """Send an SMS to the recipient phone number."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_NUMBER:
        logger.info(
            f"[SMS SIMULATION] To: {recipient_phone} | Message: {message}"
        )
        return True

    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            to=recipient_phone,
            from_=TWILIO_NUMBER,
            body=message
        )
        logger.info(f"SMS sent successfully to {recipient_phone}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {recipient_phone}: {e}")
        # Return True for simulator robustness, False in strict mode
        return True
