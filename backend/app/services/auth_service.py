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
_active_otps = {}


def normalize_phone(phone: str) -> str:
    cleaned = "".join(c for c in str(phone) if c.isdigit())
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]
    if len(cleaned) != 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit mobile number")
    return cleaned


def _mask_phone(phone: str) -> str:
    digits = "".join(c for c in str(phone) if c.isdigit())
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

    _active_otps[session_id] = otp_doc

    if settings.OTP_MODE.lower() == "development":
        logging.info("[AUTH] OTP storage: DEVELOPMENT MEMORY (session_id: %s)", _mask_session(session_id))
        return session_id
    
    if db is not None:
        try:
            await db.otps.insert_one(otp_doc)
            logging.info("[AUTH] OTP storage: SUCCESS in DB (session_id: %s)", _mask_session(session_id))
        except Exception as e:
            logging.warning("[AUTH] DB insert failed (saved in memory): %s", e)
            
    return session_id


async def _consume_otp_session(session_id: str, phone: str, otp: str, db) -> bool:
    if session_id and session_id in _active_otps:
        otp_doc = _active_otps[session_id]
        if otp_doc["phone"] == phone and not otp_doc.get("verified"):
            now = datetime.now(timezone.utc)
            if now <= otp_doc["expires_at"] and str(otp_doc["otp"]) == str(otp):
                otp_doc["verified"] = True
                if db is not None:
                    try:
                        await db.otps.update_one(
                            {"session_id": session_id},
                            {"$set": {"verified": True, "verified_at": now}}
                        )
                    except Exception:
                        pass
                return True

    if db is not None:
        try:
            query = {"phone": phone}
            if session_id:
                query["session_id"] = session_id
                
            otp_doc = await db.otps.find_one(query, sort=[("created_at", -1)])
            
            if otp_doc and not otp_doc.get("verified"):
                now = datetime.now(timezone.utc)
                expires_at = otp_doc.get("expires_at")
                
                if expires_at and expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                    
                if expires_at and now <= expires_at and str(otp_doc.get("otp")) == str(otp):
                    await db.otps.update_one(
                        {"_id": otp_doc["_id"]},
                        {"$set": {"verified": True, "verified_at": now}}
                    )
                    return True
        except Exception as e:
            logging.warning("[AUTH] DB find failed: %s", e)

    return False


def _build_fast2sms_request(phone: str, message: str, otp: int = None):
    if settings.SMS_ROUTE.lower() == "otp":
        params = {
            "route": "otp",
            "variables_values": str(otp) if otp is not None else "",
            "numbers": phone,
            "flash": int(settings.SMS_FLASH) if str(settings.SMS_FLASH).isdigit() else 0,
        }
        if settings.SMS_TEMPLATE_ID:
            params["template_id"] = settings.SMS_TEMPLATE_ID
        if settings.SMS_ENTITY_ID:
            params["entity_id"] = settings.SMS_ENTITY_ID
        return params

    params = {
        "numbers": phone,
        "message": message,
        "sender_id": settings.SMS_SENDER_ID,
        "route": settings.SMS_ROUTE,
        "language": settings.SMS_LANGUAGE,
        "flash": int(settings.SMS_FLASH) if str(settings.SMS_FLASH).isdigit() else 0,
    }
    if settings.SMS_TEMPLATE_ID:
        params["template_id"] = settings.SMS_TEMPLATE_ID
    if settings.SMS_ENTITY_ID:
        params["entity_id"] = settings.SMS_ENTITY_ID
    return params


def _extract_fast2sms_error(response_json) -> str:
    if isinstance(response_json, dict):
        msg = response_json.get("message")
        if isinstance(msg, list):
            return " ".join(str(item) for item in msg if item)
        if isinstance(msg, str) and msg:
            return msg
    elif isinstance(response_json, str):
        return response_json[:300]
    return "Fast2SMS provider error"


async def send_otp_sms(phone: str, db) -> dict:
    normalized_phone = normalize_phone(phone)
    otp = random.randint(100000, 999999)
    logging.info("[AUTH] OTP generation: SUCCESS (6-digit, not logged)")
    
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
        session_id = await _store_otp(normalized_phone, otp, db)
        logging.info("[AUTH] Final send-otp decision: SUCCESS (MOCK / DEVELOPMENT MODE)")
        return {"session_id": session_id, "dev_otp": str(otp)}

    api_key = settings.FAST_TO_SMS_API_KEY
    if not api_key:
        logging.error("[AUTH] OTP send failed: FAST_TO_SMS_API_KEY is not configured.")
        raise HTTPException(status_code=500, detail="SMS provider configuration is missing (FAST_TO_SMS_API_KEY)")

    message = f"Your verification OTP is {otp}. It is valid for 5 minutes."
    request_params = _build_fast2sms_request(normalized_phone, message, otp=otp)
    
    url = "https://www.fast2sms.com/dev/bulkV2"
    data = json.dumps(request_params).encode("utf-8")
    headers = {
        "authorization": api_key,
        "Content-Type": "application/json",
    }
    req = urllib_request.Request(url, data=data, headers=headers, method="POST")

    logging.info("[AUTH] SMS API request: SENDING to Fast2SMS bulkV2 endpoint")

    try:
        with urllib_request.urlopen(req, timeout=15) as response:
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
                error_msg = _extract_fast2sms_error(response_json)
                logging.error("[AUTH] SMS provider REJECTED request: %s. OTP not stored.", error_msg)
                raise HTTPException(status_code=400, detail=f"SMS API Error: {error_msg}")

            session_id = await _store_otp(normalized_phone, otp, db)
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
            err_msg = _extract_fast2sms_error(err_json)
        except Exception:
            err_msg = f"SMS provider error: {exc.code}"
            logging.error("[AUTH] SMS provider error body: %s", error_body[:500])

        logging.error("[AUTH] Final send-otp decision: FAILED")
        raise HTTPException(status_code=exc.code if exc.code in (400, 401, 403, 404) else 500, detail=err_msg) from exc

    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("[AUTH] SMS provider request exception: %s: %s", type(exc).__name__, str(exc))
        logging.error("[AUTH] Final send-otp decision: FAILED (Unexpected)")
        raise HTTPException(status_code=500, detail="Internal error during SMS delivery") from exc


async def verify_otp_sms(phone: str, otp: str, session_id: str, db) -> bool:
    normalized_phone = normalize_phone(phone)
    logging.info("[AUTH] verify-otp called for phone (masked): %s", _mask_phone(normalized_phone))
    logging.info("[AUTH] verify-otp session_id provided: %s", "yes" if session_id else "no")
    logging.info("[AUTH] verify-otp OTP length: %s digits", len(str(otp)))

    result = await _consume_otp_session(session_id=session_id, phone=normalized_phone, otp=otp, db=db)
    if result:
        logging.info("[AUTH] OTP verification: SUCCESS (correct, not expired, now consumed)")
    else:
        logging.warning("[AUTH] OTP verification: FAILED (wrong OTP, expired, or already consumed)")
    return result
