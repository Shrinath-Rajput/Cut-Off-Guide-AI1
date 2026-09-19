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
        logger.info(f"Email send operation: SUCCESS via Resend. Resend ID: {response.get('id', 'unknown')}")
        return
    except Exception as e:
        err_str = str(e)
        logger.warning(f"Resend send attempt to {receiver_email} failed: {err_str}. Attempting direct MX delivery...")
        
        try:
            import smtplib
            from email.message import EmailMessage

            domain = receiver_email.split("@")[-1] if "@" in receiver_email else "fouriseindia.com"
            mx_hosts = []
            try:
                import dns.resolver
                answers = dns.resolver.resolve(domain, "MX")
                mx_hosts = [str(r.exchange).rstrip(".") for r in sorted(answers, key=lambda r: r.preference)]
            except Exception as dns_err:
                logger.warning(f"DNS MX lookup failed for {domain}: {dns_err}")
                mx_hosts = ["host5.indiancloudhosting.com"]

            if not mx_hosts:
                mx_hosts = ["host5.indiancloudhosting.com"]

            msg = EmailMessage()
            msg.set_content(f"Name: {name}\nEmail: {user_email}\nSubject: {subject}\n\nMessage:\n{message_body}")
            msg["Subject"] = f"New Contact Us Submission: {subject}"
            msg["From"] = sender_email or "onboarding@resend.dev"
            msg["To"] = receiver_email
            msg["Reply-To"] = user_email

            delivered = False
            for mx in mx_hosts:
                try:
                    with smtplib.SMTP(mx, 25, timeout=15) as server:
                        server.send_message(msg)
                    logger.info(f"Email send operation: SUCCESS. Delivered directly to {receiver_email} via MX {mx}")
                    delivered = True
                    break
                except Exception as send_err:
                    logger.warning(f"Failed delivery via {mx}: {send_err}")

            if not delivered:
                raise RuntimeError(f"Could not deliver email to {receiver_email} via MX hosts: {mx_hosts}")

        except Exception as mx_err:
            logger.error(f"Delivery to {receiver_email} failed: {mx_err}")
            raise HTTPException(status_code=500, detail="Failed to send email via mail service. Please try again later.")
