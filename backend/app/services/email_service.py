import os
import resend
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def send_contact_email(name: str, user_email: str, subject: str, message_body: str):
    api_key = os.getenv("EMAIL_API_KEY")
    sender_email = os.getenv("EMAIL_FROM")
    receiver_email = os.getenv("CONTACT_RECEIVER_EMAIL")

    if not all([api_key, sender_email, receiver_email]):
        logger.error("Email service is not configured. Missing API key or configuration.")
        raise HTTPException(status_code=500, detail="Email service is not configured on the server.")

    resend.api_key = api_key

    logger.info(f"Preparing to send email via Resend to {receiver_email}")

    params = {
        "from": sender_email,
        "to": [receiver_email],
        "reply_to": user_email,
        "subject": f"New Contact Us Submission: {subject}",
        "text": f"Name: {name}\nEmail: {user_email}\nSubject: {subject}\n\nMessage:\n{message_body}"
    }

    try:
        response = resend.Emails.send(params)
        logger.info(f"Email send operation: SUCCESS. Resend ID: {response.get('id', 'unknown')}")
    except Exception as e:
        logger.error(f"Email send operation: FAILED. Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email via Resend. Please try again later.")
