from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from app.schemas.contact import ContactMessage
from app.core.database import get_db
from app.services.email_service import send_contact_email

router = APIRouter(
    prefix="/api/contact",
    tags=["Contact"]
)

@router.post("")
async def submit_contact_form(message: ContactMessage, db=Depends(get_db)) -> Dict[str, Any]:
    """
    Submit a contact form message.
    Saves the inquiry to the database.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
        
    inquiry_doc = message.model_dump() if hasattr(message, "model_dump") else message.dict()
    inquiry_doc["email"] = str(inquiry_doc["email"])
    inquiry_doc["createdAt"] = datetime.utcnow()
    inquiry_doc["status"] = "unread"
    
    try:
        await db["enquiries"].insert_one(inquiry_doc)
    except Exception as e:
        print(f"Exception during contact form insertion: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Check if it's a database connection issue
        error_msg = str(e).lower()
        if any(k in error_msg for k in ["timeout", "connection", "ssl", "tls", "refused", "network", "auth", "permission"]):
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable due to database connection issues. Please try again later."
            )
            
        raise HTTPException(status_code=500, detail="Failed to save contact message. Please try again later.")
        
    # Send email notification
    # send_contact_email raises HTTPException(status_code=500) if it fails,
    # so execution will stop here and not return success if email fails.
    send_contact_email(
        name=message.name,
        user_email=str(message.email),
        subject=message.subject,
        message_body=message.message
    )
        
    return {"message": "Contact message sent successfully"}
