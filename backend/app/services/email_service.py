import os
import smtplib
from email.message import EmailMessage
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def send_contact_email(name: str, sender_email: str, subject: str, message_body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    receiver_email = os.getenv("CONTACT_RECEIVER_EMAIL")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, receiver_email]):
        logger.error("Email service is not configured. Missing SMTP credentials.")
        raise HTTPException(status_code=500, detail="Email service is not configured on the server.")

    msg = EmailMessage()
    msg.set_content(f"Name: {name}\nEmail: {sender_email}\nSubject: {subject}\n\nMessage:\n{message_body}")
    
    msg['Subject'] = f"New Contact Us Submission: {subject}"
    msg['From'] = smtp_user
    msg['To'] = receiver_email
    msg.add_header('reply-to', sender_email)

    try:
        # Use SMTP_SSL for port 465, and STARTTLS for 587
        port = int(smtp_port)
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_host, port)
        else:
            server = smtplib.SMTP(smtp_host, port)
            server.starttls()
            
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email. Please try again later.")
