from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.schemas.contact import ContactMessage
from app.services.email_service import send_contact_email

router = APIRouter(
    prefix="/api/contact",
    tags=["Contact"]
)

@router.post("")
def submit_contact_form(message: ContactMessage) -> Dict[str, Any]:
    """
    Submit a contact form message.
    Sends an email to the configured recipient email.
    """
    send_contact_email(
        name=message.name,
        sender_email=message.email,
        subject=message.subject,
        message_body=message.message
    )
    return {"message": "Contact message sent successfully"}
