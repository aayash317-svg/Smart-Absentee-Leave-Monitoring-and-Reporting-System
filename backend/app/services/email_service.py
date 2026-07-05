import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings

logger = logging.getLogger("app.services.email")

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send an email using configured SMTP settings, or fallback to mock logging if unconfigured."""
        smtp_host = getattr(settings, "SMTP_HOST", None)
        smtp_port = getattr(settings, "SMTP_PORT", 587)
        smtp_user = getattr(settings, "SMTP_USER", None)
        smtp_pass = getattr(settings, "SMTP_PASSWORD", None)
        smtp_from = getattr(settings, "SMTP_FROM", "no-reply@attendancehub.edu")
        
        if not smtp_host or not smtp_user or not smtp_pass:
            logger.info(
                f"[MOCK EMAIL SUCCESS]\n"
                f"  From: {smtp_from}\n"
                f"  To: {to_email}\n"
                f"  Subject: {subject}\n"
                f"  Body (Preview): {body[:200]}...\n"
            )
            return True
            
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_from
            msg["To"] = to_email
            msg["Subject"] = subject
            
            mime_type = "html" if is_html else "plain"
            msg.attach(MIMEText(body, mime_type, "utf-8"))
            
            server = smtplib.SMTP(smtp_host, int(smtp_port))
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, to_email, msg.as_string())
            server.close()
            
            logger.info(f"Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMTP email to {to_email}: {str(e)}", exc_info=True)
            return False
