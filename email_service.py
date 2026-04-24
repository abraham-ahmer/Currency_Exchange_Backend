import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
SENDER_NAME = os.getenv("SENDER_NAME", "Ahmer")



def send_otp_email(recipient_email: str, otp: str) -> bool:
    """
    Send OTP code to user's email.
    
    For Gmail: Use App Password (not regular password)
    For Brevo: SMTP server is smtp-relay.brevo.com, port 587
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
        msg["To"] = recipient_email
        msg["Subject"] = "Your OTP Code for Account Verification"
        
        body = f"""
Hello,

Your One-Time Password (OTP) for account verification is:

    {otp}

This code is valid for 5 minutes. Do not share it with anyone.

If you didn't request this code, please ignore this email.

Best regards,
Currency Exchange Team
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False
