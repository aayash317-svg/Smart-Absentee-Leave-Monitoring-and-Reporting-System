"""
Unified notification service.
Orchestrates creating in-app notifications and sending corresponding emails/SMS.
"""
import datetime
from bson import ObjectId
from ..database.connection import get_db
from .email_service import send_email
from .sms_service import send_sms

def create_notification(
    recipient_user_id: str,
    title: str,
    message: str,
    notification_type: str = "Info",
    send_email_alert: bool = False,
    send_sms_alert: bool = False
) -> str:
    """
    Create an in-app notification in MongoDB and trigger optional email/SMS.
    """
    db = get_db()
    
    # Insert in-app notification
    notif_doc = {
        "recipientId": ObjectId(recipient_user_id) if isinstance(recipient_user_id, str) else recipient_user_id,
        "title": title,
        "message": message,
        "type": notification_type,
        "isRead": False,
        "createdAt": datetime.datetime.utcnow()
    }
    result = db.notifications.insert_one(notif_doc)
    
    # Get user details for sending external alerts
    user = db.users.find_one({"_id": notif_doc["recipientId"]})
    if user:
        if send_email_alert and user.get("email"):
            email_subject = f"Smart ERP Alert: {title}"
            send_email(user["email"], email_subject, message)
            
        if send_sms_alert and user.get("phone"):
            send_sms(user["phone"], f"{title}: {message}")
            
    return str(result.inserted_id)

def mark_notification_as_read(notification_id: str, user_id: str) -> bool:
    """Mark a notification as read, validating ownership."""
    db = get_db()
    from ..core.jwt import safe_object_id
    
    res = db.notifications.update_one(
        {"_id": safe_object_id(notification_id), "recipientId": safe_object_id(user_id)},
        {"$set": {"isRead": True}}
    )
    return res.modified_count > 0
