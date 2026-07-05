import logging
from ..core.config import settings

logger = logging.getLogger("app.services.sms")

class SMSService:
    @staticmethod
    def send_sms(to_phone: str, message: str) -> bool:
        """Send an SMS using Twilio integration if configured, otherwise fallback to mock print log."""
        twilio_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        twilio_auth = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        twilio_number = getattr(settings, "TWILIO_NUMBER", None)
        
        if not twilio_sid or not twilio_auth or not twilio_number:
            logger.info(
                f"[MOCK SMS SUCCESS]\n"
                f"  To: {to_phone}\n"
                f"  Message: {message}\n"
            )
            return True
            
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_auth)
            client.messages.create(
                body=message,
                from_=twilio_number,
                to=to_phone
            )
            logger.info(f"SMS successfully sent to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS via Twilio to {to_phone}: {str(e)}", exc_info=True)
            return False
