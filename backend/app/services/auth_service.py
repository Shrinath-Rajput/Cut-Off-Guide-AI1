import os
import random
import secrets
import json
import logging
import urllib.request as urllib_request
import urllib.error as urllib_error
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.core.config import settings

OTP_TTL_SECONDS = int(settings.OTP_TTL_SECONDS) if hasattr(settings, 'OTP_TTL_SECONDS') else 300


def _mask_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) >= 5:
        return "XXXXX" + digits[-5:]
    return "***"


def _mask_sender(sid: str) -> str:
    if not sid:
        return "***"
    if len(sid) >= 4:
        return sid[:2] + "***" + sid[-2:]
    return "***"


def _mask_session(sid: str) -> str:
    if not sid:
        return "***"
    if len(sid) >= 4:
        return sid[:4] + "***"
    return "***"


async def _store_otp(phone: str, otp: int, db, session_id: str = None) -> str:
    if session_id is None:
        session_id = secrets.token_hex(8)
    
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=OTP_TTL_SECONDS)
    
    otp_doc = {
        "session_id": session_id,
        "phone": phone,
        "otp": str(otp),
        "created_at": now,
        "expires_at": expires_at,
        "verified": False
    }
    
    await db.otps.insert_one(otp_doc)
    logging.info("[AUTH] OTP storage: SUCCESS (session_id: %s)", _mask_session(session_id))
    return session_id


async def _consume_otp_session(session_id: str, phone: str, otp: str, db) -> bool:
    query = {"phone": phone}
    if session_id:
        query["session_id"] = session_id
        
    otp_doc = await db.otps.find_one(query, sort=[("created_at", -1)])
    
    if not otp_doc:
        return False
        
    if otp_doc.get("verified"):
        return False
        
    now = datetime.now(timezone.utc)
    expires_at = otp_doc.get("expires_at")
    
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
        
    if now > expires_at:
        return False
        
    if str(otp_doc.get("otp")) != str(otp):
        return False
        
    await db.otps.update_one(
        {"_id": otp_doc["_id"]},
        {"$set": {"verified": True, "verified_at": now}}
    )
    return True


def _build_fast2sms_request(phone, message):
    params = {
        "numbers": phone,
        "message": message,
        "sender_id": settings.SMS_SENDER_ID,
        "route": settings.SMS_ROUTE,
        "language": settings.SMS_LANGUAGE,
        "flash": settings.SMS_FLASH,
    }
    if settings.SMS_TEMPLATE_ID:
        params["template_id"] = settings.SMS_TEMPLATE_ID
    if settings.SMS_ENTITY_ID:
        params["entity_id"] = settings.SMS_ENTITY_ID
    return params


async def send_otp_sms(phone: str, db) -> dict:
    otp = random.randint(100000, 999999)
    logging.info("[AUTH] OTP generation: SUCCESS (6-digit, not logged)")
    
    normalized_phone = phone.replace("+91", "").replace(" ", "").strip()
    if not normalized_phone.isdigit() or len(normalized_phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number format")

    if normalized_phone.startswith("91") and len(normalized_phone) == 12:
        pass
    elif len(normalized_phone) == 10:
        normalized_phone = f"91{normalized_phone}"
        
    logging.info("[AUTH] SMS provider: %s", str(settings.SMS_PROVIDER).upper())
    logging.info("[AUTH] SMS destination (masked): %s", _mask_phone(normalized_phone))
    logging.info("[AUTH] SMS route: %s", settings.SMS_ROUTE)
    logging.info("[AUTH] SMS sender_id: %s", _mask_sender(settings.SMS_SENDER_ID))
    logging.info("[AUTH] SMS template_id configured: %s", "yes" if settings.SMS_TEMPLATE_ID else "no")
    logging.info("[AUTH] SMS entity_id/pe_id configured: %s", "yes" if settings.SMS_ENTITY_ID else "no")
    
    is_development = settings.OTP_MODE.lower() == "development"
    
    if is_development:
        logging.warning(
            "[AUTH] OTP MODE = DEVELOPMENT. SMS provider call is BYPASSED. No real SMS sent. OTP stored in DB only."
        )
        session_id = await _store_otp(phone, otp, db)
        logging.info("[AUTH] Final send-otp decision: SUCCESS (MOCK / DEVELOPMENT MODE)")
        return {"session_id": session_id, "dev_otp": str(otp)}

    if settings.OTP_MODE == "production":
        if not settings.SMS_TEMPLATE_ID:
            logging.warning("[AUTH] SMS template_id is NOT configured. Indian TRAI DLT rules require an approved template_id for transactional SMS. Delivery may fail.")
        if not settings.SMS_ENTITY_ID:
            logging.warning("[AUTH] SMS entity_id/pe_id is NOT configured. Indian TRAI DLT rules require a registered Principal Entity ID. Delivery may fail.")

    api_key = settings.FAST_TO_SMS_API_KEY
    if not api_key:
        logging.error("[AUTH] OTP send failed: FAST_TO_SMS_API_KEY is not configured.")
        raise HTTPException(status_code=500, detail="SMS provider configuration is missing (FAST_TO_SMS_API_KEY)")

    message = f"Your verification OTP is {otp}. It is valid for 5 minutes."
    request_params = _build_fast2sms_request(normalized_phone, message)
    
    url = "https://www.fast2sms.com/dev/bulkV2"
    data = json.dumps(request_params).encode("utf-8")
    headers = {
        "authorization": api_key,
        "Content-Type": "application/json",
    }
    req = urllib_request.Request(url, data=data, headers=headers, method="POST")

    logging.info("[AUTH] SMS API request: SENDING to Fast2SMS bulkV2 endpoint")

    try:
        with urllib_request.urlopen(req, timeout=10) as response:
            response_text = response.read().decode("utf-8", "ignore")
            status_code = response.status
            try:
                response_json = json.loads(response_text)
            except Exception:
                response_json = response_text
                
            logging.info("[AUTH] SMS provider response HTTP status: %s", status_code)

            safe_response = {}
            if isinstance(response_json, dict):
                for k in ("return", "status", "status_code", "request_id", "message"):
                    if k in response_json:
                        safe_response[k] = response_json[k]
            else:
                safe_response = str(response_json)[:500]
            logging.info("[AUTH] SMS provider response body (safe keys only): %s", safe_response)
            
            is_success = (status_code == 200)
            if isinstance(response_json, dict) and response_json.get("return") is False:
                is_success = False

            logging.info("[AUTH] send-otp SMS delivery decision: %s", "SUCCESS" if is_success else "FAILED")
                
            if status_code != 200:
                logging.error("[AUTH] SMS provider returned non-200 HTTP status. OTP not stored.")
                raise HTTPException(status_code=500, detail="Failed to send SMS via provider (HTTP error)")
                
            if not is_success:
                error_msg = response_json.get("message", "Unknown Fast2SMS error") if isinstance(response_json, dict) else "Unknown Fast2SMS error"
                logging.error("[AUTH] SMS provider REJECTED request: %s. OTP not stored.", error_msg)
                raise HTTPException(status_code=500, detail=f"SMS API Error: {error_msg}")

            session_id = await _store_otp(phone, otp, db)
            return_data = {"session_id": session_id}
            
            if isinstance(response_json, dict) and "request_id" in response_json:
                return_data["provider_request_id"] = response_json["request_id"]
                logging.info("[AUTH] Provider accepted request. Request ID: %s", response_json["request_id"])

            logging.info("[AUTH] Final send-otp decision: SUCCESS - SMS sent via provider and OTP stored for verification")
            return return_data

    except urllib_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", "ignore")
        logging.error("[AUTH] SMS provider response HTTP status: %s", exc.code)
        try:
            err_json = json.loads(error_body)
            safe_err = {}
            if isinstance(err_json, dict):
                for k in ("return", "status", "status_code", "request_id", "message"):
                    if k in err_json:
                        safe_err[k] = err_json[k]
            else:
                safe_err = str(err_json)[:500]
            logging.error("[AUTH] SMS provider error response (safe keys only): %s", safe_err)
            err_msg = err_json.get("message", f"SMS provider error: {exc.code}")
        except Exception:
            err_msg = f"SMS provider error: {exc.code}"
            logging.error("[AUTH] SMS provider error body: %s", error_body[:500])

        logging.error("[AUTH] Final send-otp decision: FAILED")
        raise HTTPException(status_code=500, detail=err_msg) from exc

    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("[AUTH] SMS provider request exception: %s: %s", type(exc).__name__, str(exc))
        logging.error("[AUTH] Final send-otp decision: FAILED (Unexpected)")
        raise HTTPException(status_code=500, detail="Internal error during SMS delivery") from exc


async def verify_otp_sms(phone: str, otp: str, session_id: str, db) -> bool:
    logging.info("[AUTH] verify-otp called for phone (masked): %s", _mask_phone(phone))
    logging.info("[AUTH] verify-otp session_id provided: %s", "yes" if session_id else "no")
    logging.info("[AUTH] verify-otp OTP length: %s digits", len(str(otp)))

    result = await _consume_otp_session(session_id=session_id, phone=phone, otp=otp, db=db)
    if result:
        logging.info("[AUTH] OTP verification: SUCCESS (correct, not expired, now consumed)")
    else:
        logging.warning("[AUTH] OTP verification: FAILED (wrong OTP, expired, or already consumed)")
    return result
