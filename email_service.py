import os
import requests
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME")

def send_otp_email(recipient_email: str, otp: str) -> bool:
    """ Send OTP using Brevo API (works on Render)."""
    try:
        body = f"""
Hello,

Your One-Time Password (OTP) for account verification is:

    {otp}

This code is valid for 5 minutes. Do not share it with anyone.

If you didn't request this code, please ignore this email.

Best regards,
Currency Exchange Team
        """

        data = {
            "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
            "to": [{"email": recipient_email}],
            "subject": "Your OTP Code for Account Verification",
            "textContent": body
        }

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
            json=data
        )

        return response.status_code == 201
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False

