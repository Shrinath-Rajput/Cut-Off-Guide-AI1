from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import secrets

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import UserLogin, UserCreate, UserResponse
from app.services.auth_service import send_otp_sms, verify_otp_sms
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class OtpRequest(BaseModel):
    name: str
    email: str
    phone: str

class OtpVerifyRequest(OtpRequest):
    otp: str
    sessionId: str

async def create_or_update_user(payload: UserLogin, db):
    collection = db["users"]
    
    uid = payload.uid
    if not uid:
        if payload.phone:
            uid = f"{payload.provider}-{payload.phone}"
        elif payload.email:
            uid = f"{payload.provider}-{payload.email}"
        else:
            uid = f"{payload.provider}-{secrets.token_hex(6)}"

    now = datetime.now(timezone.utc)
    
    filter_query = {"uid": uid}
    if payload.email:
        filter_query = {"$or": [{"uid": uid}, {"email": payload.email}]}
        
    existing_user = await collection.find_one(filter_query)
    
    if existing_user:
        await collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {
                "name": payload.name or existing_user.get("name", "User"),
                "email": payload.email or existing_user.get("email", ""),
                "phone": payload.phone or existing_user.get("phone", ""),
                "provider": payload.provider or existing_user.get("provider", "phone"),
                "photoURL": payload.photoURL or existing_user.get("photoURL", ""),
                "lastLogin": now
            }}
        )
        updated_user = await collection.find_one({"_id": existing_user["_id"]})
        updated_user["id"] = str(updated_user["_id"])
        del updated_user["_id"]
        
        token = create_access_token(subject=uid, role=updated_user.get("role", "USER"))
        return {
            "status": "success",
            "message": "User authenticated",
            "token": token,
            "user": updated_user
        }
        
    new_user = {
        "uid": uid,
        "name": payload.name or "User",
        "email": payload.email,
        "phone": payload.phone,
        "provider": payload.provider or "phone",
        "photoURL": payload.photoURL,
        "role": "USER",
        "createdAt": now,
        "lastLogin": now
    }
    result = await collection.insert_one(new_user)
    new_user["id"] = str(result.inserted_id)
    if "_id" in new_user:
        del new_user["_id"]
    
    token = create_access_token(subject=uid, role="USER")
    return {
        "status": "success",
        "message": "User registered",
        "token": token,
        "user": new_user
    }


@router.post("/send-otp")
async def send_otp(request: OtpRequest, db=Depends(get_db)):
    from fastapi.responses import JSONResponse
    try:
        result = await send_otp_sms(request.phone, db)
        response_data = {"status": "success", "message": "OTP sent successfully", "sessionId": result["session_id"]}
        if result.get("dev_otp"):
            response_data["dev_otp"] = result["dev_otp"]
        if result.get("provider_request_id"):
            response_data["provider_request_id"] = result["provider_request_id"]
        return response_data
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})

@router.post("/verify-otp")
async def verify_otp(request: OtpVerifyRequest, db=Depends(get_db)):
    try:
        is_valid = await verify_otp_sms(request.phone, request.otp, request.sessionId, db)
        if not is_valid:
            raise HTTPException(status_code=400, detail="OTP is invalid or expired")
            
        user_payload = UserLogin(
            uid=f"phone-{request.phone}",
            name=request.name,
            email=request.email,
            phone=request.phone,
            provider="phone"
        )
        return await create_or_update_user(user_payload, db)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register(request: UserLogin):
    db = get_db()
    return await create_or_update_user(request, db)

@router.post("/login")
async def login(request: UserLogin):
    db = get_db()
    return await create_or_update_user(request, db)

@router.post("/google")
async def google_auth(request: UserLogin):
    db = get_db()
    return await create_or_update_user(request, db)
