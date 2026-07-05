import datetime
import logging
from bson.objectid import ObjectId
from ..database.connection import get_db
from .email_service import EmailService
from .sms_service import SMSService

logger = logging.getLogger("app.services.notifications")

class NotificationService:
    @staticmethod
    async def create_notification(
        recipient_id: str,
        title: str,
        message: str,
        notify_email: bool = False,
        notify_sms: bool = False,
        email_addr: str = None,
        phone_no: str = None
    ) -> str:
        """Create an in-app notification document and optionally send SMTP email / SMS warning."""
        db = get_db()
        
        # Convert recipient ID string to ObjectId safely
        rec_id = recipient_id
        if isinstance(recipient_id, str) and ObjectId.is_valid(recipient_id):
            rec_id = ObjectId(recipient_id)
            
        notification_doc = {
            "recipientId": rec_id,
            "title": title,
            "message": message,
            "isRead": False,
            "createdAt": datetime.datetime.utcnow(),
            "isDeleted": False
        }
        
        try:
            res = await db.notifications.insert_one(notification_doc)
            notif_id = str(res.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert notification record in MongoDB: {str(e)}")
            notif_id = ""
            
        # Dispatch email if requested and recipient email address is valid
        if notify_email and email_addr:
            EmailService.send_email(
                to_email=email_addr,
                subject=title,
                body=f"Hello,\n\n{message}\n\nBest regards,\nSmart Absentee Leave Monitoring System"
            )
            
        # Dispatch SMS if requested and recipient phone number is valid
        if notify_sms and phone_no:
            SMSService.send_sms(
                to_phone=phone_no,
                message=f"[{title}] {message}"
            )
            
        return notif_id
