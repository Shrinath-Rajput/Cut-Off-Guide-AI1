import json
import logging
import os
import random
import re
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from dotenv import load_dotenv
from flask import Blueprint, jsonify, redirect, request

from config import get_users_collection

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
except ImportError:  # pragma: no cover
    firebase_admin = None
    firebase_auth = None

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

FAST_TO_SMS_API_KEY = os.getenv("FAST_TO_SMS_API_KEY")
OTP_MODE = (os.getenv("OTP_MODE", "development") or "development").strip().lower()
COMPANY_GOOGLE_AUTH_URL = os.getenv("COMPANY_GOOGLE_AUTH_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv(
    "GOOGLE_OAUTH_REDIRECT_URI",
    "http://localhost:5000/api/auth/google/callback",
)
FRONTEND_APP_URL = os.getenv("FRONTEND_APP_URL", "http://localhost:5173")
OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "300"))

SMS_PROVIDER = (os.getenv("SMS_PROVIDER", "fast2sms") or "fast2sms").strip().lower()
SMS_SENDER_ID = (os.getenv("SMS_SENDER_ID", "FSTSMS") or "FSTSMS").strip()
SMS_ROUTE = (os.getenv("SMS_ROUTE", "q") or "q").strip().lower()
SMS_TEMPLATE_ID = (os.getenv("SMS_TEMPLATE_ID") or "").strip()
SMS_ENTITY_ID = (os.getenv("SMS_ENTITY_ID") or os.getenv("SMS_PE_ID") or "").strip()
SMS_LANGUAGE = (os.getenv("SMS_LANGUAGE", "english") or "english").strip().lower()
SMS_FLASH = (os.getenv("SMS_FLASH", "0") or "0").strip()

OTP_SESSIONS = {}
OTP_PHONE_LOOKUPS = {}
OTP_LOCK = threading.Lock()


def _initialize_firebase_admin():
    if firebase_admin is None:
        return False

    if firebase_admin._apps:
        return True

    try:
        firebase_admin.initialize_app()
        return True
    except Exception:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            try:
                account_info = json.loads(service_account_json)
                firebase_admin.initialize_app(
                    credentials=firebase_admin.credentials.Certificate(account_info),
                    options={"projectId": account_info.get("project_id")},
                )
                return True
            except Exception:
                logging.exception("Firebase Admin initialization with service account JSON failed")
                return False

        firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
        if firebase_project_id:
            try:
                firebase_admin.initialize_app(options={"projectId": firebase_project_id})
                return True
            except Exception:
                logging.exception("Firebase Admin initialization with project ID failed")
                return False

        return False


def _verify_firebase_id_token(id_token):
    if not id_token:
        raise ValueError("Firebase ID token is missing")

    if firebase_admin is None or firebase_auth is None:
        raise RuntimeError("Firebase Admin SDK is not installed")

    if not _initialize_firebase_admin():
        raise RuntimeError("Firebase Admin is not configured on the backend")

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as exc:
        raise ValueError("Invalid or expired Firebase ID token") from exc


def build_otp_sms_message(otp):
    return f"Your verification OTP is {otp}. It is valid for 5 minutes."


def build_fast2sms_bulk_request(phone, message, otp=None):
    """
    Build Fast2SMS bulkV2 request payload.

    Fast2SMS route documentation note from provider response:
      - route "otp"  : DOES NOT accept free-form "message"; requires:
          * variables_values = numeric OTP digits only (comma-separated for multiple vars
          * template_id          = registered OTP template
          * numbers, sender_id, route=otp
      - route "q" / "t" / "dlt" / "p" : use free-form "message"
    
    IMPORTANT: For SMS_ROUTE="q", the request should NOT include sender_id to match
    the proven Fast2SMS bulkV2 API contract that was working before backend integration.
    """
    if SMS_ROUTE == "otp":
        params = {
            "numbers": phone,
            "route": "otp",
            "sender_id": SMS_SENDER_ID,
            "variables_values": str(otp) if otp is not None else "",
        }
        if SMS_TEMPLATE_ID:
            params["template_id"] = SMS_TEMPLATE_ID
        if SMS_ENTITY_ID:
            params["entity_id"] = SMS_ENTITY_ID
        return params

    # For route "q" (Quick/Transactional), use the minimal proven request format
    # that was successfully sending real SMS before backend integration
    if SMS_ROUTE == "q":
        return {
            "numbers": phone,
            "message": message,
            "sender_id": SMS_SENDER_ID,
            "route": "q",
            "language": SMS_LANGUAGE,
            "flash": SMS_FLASH,
        }

    # For other routes (dlt, t, p), include full configuration
    params = {
        "numbers": phone,
        "message": message,
        "sender_id": SMS_SENDER_ID,
        "route": SMS_ROUTE,
        "language": SMS_LANGUAGE,
        "flash": SMS_FLASH,
    }
    if SMS_TEMPLATE_ID:
        params["template_id"] = SMS_TEMPLATE_ID
    if SMS_ENTITY_ID:
        params["entity_id"] = SMS_ENTITY_ID
    return params


def validate_fast2sms_production_config():
    if OTP_MODE != "production":
        return

    if not FAST_TO_SMS_API_KEY:
        raise RuntimeError("FAST_TO_SMS_API_KEY is not configured")

    if SMS_ROUTE == "otp" and not SMS_TEMPLATE_ID:
        raise RuntimeError(
            "SMS_ROUTE=otp requires SMS_TEMPLATE_ID to be set in backend/.env. "
            "Register an approved OTP template on Fast2SMS and paste its ID into the .env file."
        )

    if SMS_SENDER_ID.upper() == "FSTSMS":
        logging.warning(
            "[AUTH] SMS sender_id is using the generic Fast2SMS test sender 'FSTSMS'. For real India delivery, "
            "replace it with a DLT-registered sender ID in backend/.env."
        )


def is_fast2sms_success(parsed_response=None, status_code=None, body=None):
    if isinstance(parsed_response, dict):
        message_value = parsed_response.get("message")
        if isinstance(message_value, list):
            message_value = " ".join(str(item) for item in message_value if item)
        message_text = " ".join(
            str(value)
            for value in [
                message_value,
                parsed_response.get("status"),
                parsed_response.get("status_code"),
                parsed_response.get("return"),
            ]
            if value is not None
        ).lower()
        rejection_markers = (
            "blocked",
            "dnd",
            "rejected",
            "invalid",
            "insufficient",
            "wallet balance",
            "wallet",
            "unauthorized",
            "authentication",
            "template",
            "sender",
            "not sent",
            "failed",
            "failure",
            "error",
            "not delivered",
        )
        if any(marker in message_text for marker in rejection_markers):
            return False

        return_value = parsed_response.get("return")
        if return_value is False or str(return_value).lower() in {"false", "0"}:
            return False

        status_value = str(parsed_response.get("status", "")).lower()
        if status_value in {"false", "fail", "failed", "error", "rejected"}:
            return False

    if status_code is not None:
        try:
            status_int = int(status_code)
            if not (200 <= status_int < 300):
                return False
        except (TypeError, ValueError):
            pass

    if isinstance(parsed_response, dict):
        return_value = parsed_response.get("return")
        if return_value in (True, "true", "True", "1", 1):
            return True
        if str(parsed_response.get("status", "")).lower() == "success":
            return True
        message_value = parsed_response.get("message")
        if isinstance(message_value, list):
            message_value = " ".join(str(item) for item in message_value if item)
        if isinstance(message_value, str) and "success" in message_value.lower():
            return True
        if parsed_response.get("request_id"):
            return True

    if isinstance(body, str):
        lowered = body.lower()
        if "sms sent successfully" in lowered or "request_id" in lowered:
            return True

    return False


def format_fast2sms_error_message(parsed_response=None, status_code=None, body=None):
    details = []

    if status_code is not None:
        details.append(f"HTTP {status_code}")

    if isinstance(parsed_response, dict):
        provider_status = parsed_response.get("status_code")
        if provider_status is not None and "HTTP" not in " ".join(details):
            details.append(f"HTTP {provider_status}")

        message = parsed_response.get("message")
        if isinstance(message, list):
            message = " ".join(str(item) for item in message if item)
        if message:
            details.append(str(message))
    elif body:
        details.append(str(body))

    if not details:
        details.append("Unknown Fast2SMS provider error")

    return f"Fast2SMS rejected the OTP request: {' | '.join(details)}"


def _sanitize_fast2sms_payload(payload):
    if isinstance(payload, dict):
        allowed = {}
        for key in ("return", "status", "status_code", "request_id", "message"):
            if key in payload:
                value = payload[key]
                if isinstance(value, list):
                    value = " ".join(str(item) for item in value if item)
                if isinstance(value, str):
                    value = value[:500]
                allowed[key] = value
        return allowed
    if isinstance(payload, str):
        return payload[:500]
    return payload


def register_routes(app):
    api = Blueprint("api", __name__, url_prefix="/api")

    def create_or_update_user(payload):
        uid = (payload.get("uid") or "").strip()
        if not uid:
            phone = (payload.get("phone") or "").strip()
            email = (payload.get("email") or "").strip().lower()
            provider = (payload.get("provider") or "phone").strip()
            if phone:
                uid = f"{provider}-{phone}"
            elif email:
                uid = f"{provider}-{email}"
            else:
                uid = f"{provider}-{secrets.token_hex(6)}"

        name = (payload.get("name") or "User").strip()
        email = (payload.get("email") or "").strip().lower()
        phone = (payload.get("phone") or "").strip()
        provider = (payload.get("provider") or "phone").strip()
        photo_url = (payload.get("photoURL") or payload.get("photo") or "").strip()

        collection = get_users_collection()
        if collection is None:
            return jsonify({"status": "error", "message": "MongoDB is unavailable"}), 503

        now = datetime.now(timezone.utc)
        filter_query = {"uid": uid}
        if email:
            filter_query = {"$or": [{"uid": uid}, {"email": email}]}

        existing_user = collection.find_one(filter_query)
        if existing_user:
            collection.update_one(
                {"_id": existing_user["_id"]},
                {
                    "$set": {
                        "name": name or existing_user.get("name", "User"),
                        "email": email or existing_user.get("email", ""),
                        "phone": phone or existing_user.get("phone", ""),
                        "provider": provider or existing_user.get("provider", "phone"),
                        "photoURL": photo_url or existing_user.get("photoURL", ""),
                        "lastLogin": now,
                    }
                },
            )
            updated_user = collection.find_one({"_id": existing_user["_id"]})
            updated_user["_id"] = str(updated_user["_id"])
            # Also include a stable `id` field for frontend convenience
            updated_user["id"] = updated_user["_id"]
            return jsonify(
                {
                    "status": "success",
                    "message": "User authenticated",
                    "token": f"token-{uid}",
                    "user": updated_user,
                }
            )

        new_user = {
            "uid": uid,
            "name": name,
            "email": email,
            "phone": phone,
            "provider": provider,
            "photoURL": photo_url,
            "createdAt": now,
            "lastLogin": now,
        }
        result = collection.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        new_user["id"] = new_user["_id"]
        return jsonify(
            {
                "status": "success",
                "message": "User registered",
                "token": f"token-{uid}",
                "user": new_user,
            }
        )

    def _normalize_phone_for_sms(phone):
        digits = re.sub(r"\D", "", phone or "")
        if not digits:
            return ""

        # Local 10-digit Indian number -> prepend country code
        if len(digits) == 10:
            return f"91{digits}"

        # Leading 0 followed by 10 digits -> drop leading zero and prepend country code
        if digits.startswith("0") and len(digits) == 11:
            return f"91{digits[1:]}"

        # Already includes country code (e.g. 91xxxxxxxxxx)
        if digits.startswith("91") and len(digits) == 12:
            return digits

        # Fall back: accept numbers between 11 and 15 digits (international style)
        if 11 <= len(digits) <= 15:
            return digits

        return ""

    def _build_google_auth_url():
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib_parse.urlencode(params)

    def _exchange_google_code(code):
        token_url = "https://oauth2.googleapis.com/token"
        data = urllib_parse.urlencode(
            {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
        ).encode("utf-8")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_obj = urllib_request.Request(token_url, data=data, headers=headers, method="POST")
        with urllib_request.urlopen(request_obj, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def _fetch_google_user_info(access_token):
        request_obj = urllib_request.Request(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            method="GET",
        )
        with urllib_request.urlopen(request_obj, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def _build_frontend_callback_url(token, user):
        query = urllib_parse.urlencode(
            {
                "token": token,
                "uid": user.get("uid", ""),
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "photoURL": user.get("photoURL", ""),
            }
        )
        return f"{FRONTEND_APP_URL}/auth/google/callback?{query}"

    def _send_fast2sms_otp(phone, otp):
        if not FAST_TO_SMS_API_KEY:
            raise RuntimeError("FAST_TO_SMS_API_KEY is not configured")

        normalized_phone = _normalize_phone_for_sms(phone)
        if not normalized_phone:
            raise RuntimeError("Phone number is required")

        message = build_otp_sms_message(otp)
        validate_fast2sms_production_config()

        if SMS_ROUTE == "otp" and not SMS_TEMPLATE_ID:
            logging.error(
                "[AUTH] SMS_ROUTE=otp was selected but SMS_TEMPLATE_ID is empty. "
                "Fast2SMS route='otp' REQUIRES a pre-registered OTP template ID. "
                "Either set SMS_TEMPLATE_ID in .env, or change SMS_ROUTE to 'q' (Quick/Transactional route) for free-form text SMS."
            )
            raise RuntimeError(
                "SMS_ROUTE=otp requires SMS_TEMPLATE_ID to be set in backend/.env. "
                "Either register an OTP template on the Fast2SMS dashboard and paste its ID into SMS_TEMPLATE_ID=, "
                "or change SMS_ROUTE=q to use the transactional Quick route instead."
            )

        request_params = build_fast2sms_bulk_request(normalized_phone, message, otp=otp)

        logging.info("[OTP DEBUG] OTP generated")
        logging.info("[OTP DEBUG] SMS provider request started")
        logging.info("[AUTH] SMS provider: %s", SMS_PROVIDER.upper())
        logging.info("[AUTH] SMS route: %s", SMS_ROUTE)
        if SMS_ROUTE == "otp":
            logging.info("[AUTH] SMS payload style: OTP route (variables_values + template_id)")
        else:
            logging.info("[AUTH] SMS payload style: transactional route (free-form message)")
        if SMS_SENDER_ID and SMS_ROUTE != "q":
            logging.info("[AUTH] SMS sender_id: %s (masked: %s)", SMS_SENDER_ID[:2] + "***" + SMS_SENDER_ID[-2:] if len(SMS_SENDER_ID) >= 4 else "***", "yes" if SMS_SENDER_ID else "no")
        if SMS_TEMPLATE_ID:
            logging.info("[AUTH] SMS template_id configured: %s", "yes")
        if SMS_ENTITY_ID:
            logging.info("[AUTH] SMS entity_id/pe_id configured: %s", "yes")
        logging.info("[AUTH] SMS destination (masked): %s", "XXXXX" + normalized_phone[-5:] if len(normalized_phone) >= 5 else "***")

        if OTP_MODE == "production":
            if SMS_ROUTE == "otp" and not SMS_TEMPLATE_ID:
                logging.warning("[AUTH] SMS_ROUTE=otp requires template_id. Delivery may fail.")
            elif SMS_ROUTE != "q" and not SMS_TEMPLATE_ID:
                logging.warning("[AUTH] SMS template_id is NOT configured. For DLT-compliant delivery in India, register and configure a template_id.")
            if SMS_ROUTE != "q" and not SMS_ENTITY_ID:
                logging.warning("[AUTH] SMS entity_id/pe_id is NOT configured. For DLT-compliant delivery in India, register and configure entity_id.")

        url = "https://www.fast2sms.com/dev/bulkV2"
        data = json.dumps(request_params).encode("utf-8")
        headers = {
            "authorization": FAST_TO_SMS_API_KEY,
            "Content-Type": "application/json",
        }
        req = urllib_request.Request(url, data=data, headers=headers, method="POST")

        logging.info("[AUTH] SMS API request: SENDING to Fast2SMS bulkV2 endpoint")
        logging.info("[OTP DEBUG] Fast2SMS call starting")

        try:
            with urllib_request.urlopen(req, timeout=20) as response:
                response_text = response.read().decode("utf-8", "ignore")
                status_code = response.status
                try:
                    response_json = json.loads(response_text)
                except Exception:
                    response_json = response_text

                safe_response = _sanitize_fast2sms_payload(response_json)
                logging.info("[OTP DEBUG] Fast2SMS HTTP status: %s", status_code)
                logging.info("[OTP DEBUG] Fast2SMS response: %s", safe_response)
                success = is_fast2sms_success(response_json, status_code, response_text)
                logging.info("[OTP DEBUG] Fast2SMS success decision: %s", str(success).lower())
                logging.info("[OTP DEBUG] SMS provider response received")
                logging.info("[OTP DEBUG] Provider HTTP status: %s", status_code)
                logging.info("[AUTH] SMS provider response body (safe keys only): %s", safe_response)
                logging.info("[OTP DEBUG] OTP request completed")

                return {"status_code": status_code, "body": response_text}
        except urllib_error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", "ignore")
            try:
                error_json = json.loads(error_body)
            except Exception:
                error_json = error_body

            safe_err = _sanitize_fast2sms_payload(error_json)
            logging.info("[OTP DEBUG] Fast2SMS HTTP status: %s", exc.code)
            logging.info("[OTP DEBUG] Fast2SMS response: %s", safe_err)
            logging.info("[OTP DEBUG] Fast2SMS success decision: %s", "false")
            logging.info("[OTP DEBUG] SMS provider response received")
            logging.info("[OTP DEBUG] Provider HTTP status: %s", exc.code)
            logging.info("[AUTH] SMS provider error response (safe keys only): %s", safe_err)
            logging.info("[OTP DEBUG] OTP request completed")

            raise RuntimeError(f"Fast2SMS request failed with HTTP {exc.code}: {error_body}") from exc
        except Exception as exc:
            logging.info("[OTP DEBUG] Fast2SMS HTTP status: %s", "error")
            logging.info("[OTP DEBUG] Fast2SMS response: %s", str(exc)[:500])
            logging.info("[OTP DEBUG] Fast2SMS success decision: %s", "false")
            logging.info("[OTP DEBUG] SMS provider response received")
            logging.info("[OTP DEBUG] Provider response: %s", str(exc)[:500])
            logging.info("[AUTH] SMS provider request exception: %s: %s", type(exc).__name__, str(exc))
            logging.info("[OTP DEBUG] OTP request completed")
            raise RuntimeError(f"Fast2SMS request failed: {exc}") from exc

    def _store_otp(phone, otp, session_id=None):
        if session_id is None:
            session_id = secrets.token_hex(8)

        expires_at = int(datetime.now(timezone.utc).timestamp()) + OTP_TTL_SECONDS
        with OTP_LOCK:
            OTP_SESSIONS[session_id] = {"phone": phone, "otp": otp, "expires_at": expires_at}
            OTP_PHONE_LOOKUPS[phone] = session_id

        return session_id

    def _delete_otp_session(session_id=None, phone=None):
        with OTP_LOCK:
            if session_id:
                OTP_SESSIONS.pop(session_id, None)
            if phone:
                phone_session_id = OTP_PHONE_LOOKUPS.pop(phone, None)
                if phone_session_id and phone_session_id != session_id:
                    OTP_SESSIONS.pop(phone_session_id, None)

    def _get_otp_session(session_id=None, phone=None):
        now = int(datetime.now(timezone.utc).timestamp())
        with OTP_LOCK:
            if session_id:
                entry = OTP_SESSIONS.get(session_id)
                if entry and entry.get("expires_at", 0) >= now:
                    return entry

            if phone:
                phone_session_id = OTP_PHONE_LOOKUPS.get(phone)
                if phone_session_id:
                    entry = OTP_SESSIONS.get(phone_session_id)
                    if entry and entry.get("expires_at", 0) >= now:
                        return entry

            return None

    def _consume_otp_session(session_id=None, phone=None, otp=None):
        with OTP_LOCK:
            entry = None
            if session_id:
                entry = OTP_SESSIONS.get(session_id)
            if not entry and phone:
                phone_session_id = OTP_PHONE_LOOKUPS.get(phone)
                if phone_session_id:
                    entry = OTP_SESSIONS.get(phone_session_id)

            if not entry:
                return False

            now = int(datetime.now(timezone.utc).timestamp())
            if entry.get("expires_at", 0) < now:
                OTP_SESSIONS.pop(session_id, None)
                OTP_PHONE_LOOKUPS.pop(phone, None)
                return False

            if otp is not None and str(entry.get("otp")) != str(otp):
                return False

            OTP_SESSIONS.pop(session_id, None)
            OTP_PHONE_LOOKUPS.pop(phone, None)
            return True

    @api.route("/")
    def home():
        return {
            "status": "success",
            "message": "CutOff Guide Backend Running Successfully",
        }

    @api.route("/health")
    def health_check():
        return {"status": "healthy"}

    @api.route("/auth/send-otp", methods=["POST"])
    def send_otp():
        payload = request.get_json(silent=True) or {}
        logging.info("[OTP DEBUG] send-otp request received")
        logging.info("[AUTH] send-otp endpoint reached: payload keys=%s", sorted(payload.keys()))
        logging.info("[AUTH] OTP_MODE value: %s", repr(OTP_MODE))
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        phone = (payload.get("phone") or "").strip()

        if not name:
            return jsonify({"status": "error", "message": "Name is required"}), 400
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
        if not phone:
            return jsonify({"status": "error", "message": "Phone is required"}), 400
        normalized_phone = _normalize_phone_for_sms(phone)
        if not normalized_phone:
            return jsonify({"status": "error", "message": "Phone number is invalid"}), 400

        logging.info("[AUTH] send-otp called for phone (masked): %s", "XXXXX" + normalized_phone[-5:] if len(normalized_phone) >= 5 else "***")
        logging.info("[AUTH] OTP generation started")

        otp = random.randint(100000, 999999)
        logging.info("[AUTH] OTP generation succeeded: generated 6-digit code (value NOT logged)")

        if OTP_MODE == "development":
            session_id = _store_otp(normalized_phone, otp)
            logging.warning(
                "[AUTH] OTP MODE = DEVELOPMENT. SMS provider call is BYPASSED. No real SMS sent. OTP stored in memory only."
            )
            logging.info("[AUTH] OTP storage started")
            logging.info("[AUTH] OTP storage succeeded (session_id: %s...)", session_id[:4] + "***" if len(session_id) >= 4 else "***")
            logging.info("[AUTH] Final send-otp decision: SUCCESS (MOCK / DEVELOPMENT MODE)")
            return jsonify(
                {
                    "status": "success",
                    "message": "OTP sent successfully in development mode (check backend logs)",
                    "sessionId": session_id,
                    "dev_otp": str(otp),
                    "_otp_mode_debug": OTP_MODE,
                }
            )

        if not FAST_TO_SMS_API_KEY:
            logging.error("[AUTH] OTP send failed: FAST_TO_SMS_API_KEY is not configured in backend/.env")
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "SMS provider configuration is missing/invalid.",
                        "requiredEnvVars": ["FAST_TO_SMS_API_KEY", "SMS_PROVIDER", "SMS_SENDER_ID", "SMS_ROUTE"],
                    }
                ),
                503,
            )

        session_id = _store_otp(normalized_phone, otp)
        logging.info("[AUTH] OTP storage succeeded (session_id: %s...)", session_id[:4] + "***" if len(session_id) >= 4 else "***")

        try:
            logging.info("[AUTH] OTP storage started")
            resp = _send_fast2sms_otp(normalized_phone, otp)
            status_code = None
            body = None
            parsed = None

            if isinstance(resp, dict):
                status_code = resp.get("status_code")
                body = resp.get("body")
                try:
                    parsed = json.loads(body) if body else None
                except Exception:
                    parsed = None

            logging.info("[DEBUG] Fast2SMS response: status_code=%s, parsed=%s", status_code, parsed)

            success = is_fast2sms_success(parsed, status_code, body)
            logging.info("[AUTH] SMS provider response/status: status_code=%s parsed=%s", status_code, parsed)
            logging.info("[AUTH] send-otp SMS delivery decision: %s", "SUCCESS" if success else "FAILED")
            logging.info("[OTP DEBUG] Fast2SMS success decision: %s", str(success).lower())

            if not success:
                _delete_otp_session(session_id=session_id, phone=normalized_phone)
                error_message = format_fast2sms_error_message(parsed, status_code, body)
                logging.error("[AUTH] SMS provider rejected the OTP request: %s", error_message)
                logging.error("[AUTH] OTP storage: REMOVED (provider did not accept SMS)")
                logging.error("[AUTH] Final send-otp decision: FAILED")
                logging.info("[OTP DEBUG] Final Flask status: %s", 503)
                return jsonify({
                    "status": "error",
                    "message": error_message,
                    "provider": "fast2sms",
                    "provider_status_code": status_code,
                    "requiredEnvVars": ["FAST_TO_SMS_API_KEY", "SMS_PROVIDER", "SMS_SENDER_ID", "SMS_ROUTE"],
                }), 503
        except RuntimeError as exc:
            _delete_otp_session(session_id=session_id, phone=normalized_phone)
            logging.exception("[AUTH] SMS provider raised an exception while sending OTP")
            logging.error("[AUTH] Final send-otp decision: FAILED (RuntimeError)")
            message = str(exc)
            lowered = message.lower()
            if "wallet balance" in lowered or "insufficient wallet" in lowered:
                provider_message = "Fast2SMS rejected the OTP request because the account wallet balance is insufficient."
            elif "dnd" in lowered or "blocked" in lowered:
                provider_message = "Fast2SMS rejected the OTP request because the destination number is blocked or DND restricted."
            else:
                provider_message = "Fast2SMS rejected the OTP request."
            return jsonify({
                "status": "error",
                "message": provider_message,
                "provider": "fast2sms",
                "provider_error": message,
                "requiredEnvVars": ["FAST_TO_SMS_API_KEY", "SMS_PROVIDER", "SMS_SENDER_ID", "SMS_ROUTE"],
            }), 503
        except Exception:
            _delete_otp_session(session_id=session_id, phone=normalized_phone)
            logging.exception("[AUTH] Unexpected OTP send failure")
            logging.error("[AUTH] Final send-otp decision: FAILED (Unexpected)")
            return jsonify(
                {
                    "status": "error",
                    "message": "Unexpected backend error during OTP send.",
                    "provider": "fast2sms",
                    "requiredEnvVars": ["FAST_TO_SMS_API_KEY", "SMS_PROVIDER", "SMS_SENDER_ID", "SMS_ROUTE"],
                }
            ), 503

        logging.info("[AUTH] Final send-otp decision: SUCCESS - SMS sent via provider and OTP stored for verification")
        logging.info("[OTP DEBUG] Final Flask status: %s", 200)
        return jsonify({"status": "success", "message": "OTP sent successfully", "sessionId": session_id})

    @api.route("/auth/verify-otp", methods=["POST"])
    def verify_otp():
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        phone = (payload.get("phone") or "").strip()
        otp = (payload.get("otp") or "").strip()
        session_id = (payload.get("sessionId") or "").strip()

        if not name:
            return jsonify({"status": "error", "message": "Name is required"}), 400
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
        if not phone:
            return jsonify({"status": "error", "message": "Phone is required"}), 400
        if not otp:
            return jsonify({"status": "error", "message": "OTP is required"}), 400
        normalized_phone = _normalize_phone_for_sms(phone)
        if not normalized_phone:
            return jsonify({"status": "error", "message": "Phone number is invalid"}), 400

        logging.info("[AUTH] verify-otp called for phone (masked): %s", "XXXXX" + normalized_phone[-5:] if len(normalized_phone) >= 5 else "***")
        logging.info("[AUTH] verify-otp session_id provided: %s", "yes" if session_id else "no")
        logging.info("[AUTH] verify-otp OTP length: %s digits", len(otp))

        if not _consume_otp_session(session_id=session_id, phone=normalized_phone, otp=otp):
            logging.warning("[AUTH] OTP verification: FAILED (wrong OTP, expired, or already consumed)")
            return jsonify({"status": "error", "message": "OTP is invalid or expired"}), 400

        logging.info("[AUTH] OTP verification: SUCCESS (correct, not expired, now consumed)")

        user_payload = {
            "uid": f"phone-{normalized_phone}",
            "name": name,
            "email": email,
            "phone": normalized_phone,
            "provider": "phone",
        }
        result = create_or_update_user(user_payload)
        logging.info("[AUTH] User create/update: COMPLETE after OTP verification")
        return result

    @api.route("/auth/login", methods=["POST"])
    def login_user():
        payload = request.get_json(silent=True) or {}
        return create_or_update_user(payload)

    @api.route("/auth/google", methods=["GET", "POST"])
    def google_auth():
        if request.method == "GET":
            if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
                return redirect(_build_google_auth_url())

            if COMPANY_GOOGLE_AUTH_URL:
                return redirect(COMPANY_GOOGLE_AUTH_URL)

            missing_vars = []
            if not GOOGLE_CLIENT_ID:
                missing_vars.append("GOOGLE_CLIENT_ID")
            if not GOOGLE_CLIENT_SECRET:
                missing_vars.append("GOOGLE_CLIENT_SECRET")
            if not COMPANY_GOOGLE_AUTH_URL:
                missing_vars.append("COMPANY_GOOGLE_AUTH_URL")

            return (
                jsonify(
                    {
                        "status": "error",
                        "message": (
                            "Google OAuth credentials are not configured. "
                            "Set "
                            + ", ".join(missing_vars)
                            + " in backend .env."
                        ),
                    }
                ),
                501,
            )

        payload = request.get_json(silent=True) or {}
        firebase_id_token = (payload.get("idToken") or payload.get("token") or "").strip()

        if not firebase_id_token:
            legacy_google_payload = {
                "uid": payload.get("uid") or payload.get("user_id") or "",
                "name": payload.get("name") or "Google User",
                "email": (payload.get("email") or "").strip().lower(),
                "provider": "google",
                "photoURL": payload.get("photoURL") or payload.get("picture") or "",
            }
            if legacy_google_payload["uid"] and legacy_google_payload["email"]:
                return create_or_update_user(legacy_google_payload)
            return jsonify({
                "status": "error",
                "message": "Firebase Google ID token is missing or invalid.",
            }), 401

        try:
            decoded_firebase_user = _verify_firebase_id_token(firebase_id_token)
        except RuntimeError as exc:
            logging.exception("Google Firebase token verification setup error")
            return jsonify({
                "status": "error",
                "message": str(exc),
            }), 503
        except ValueError as exc:
            return jsonify({
                "status": "error",
                "message": str(exc),
            }), 401

        email = (decoded_firebase_user.get("email") or payload.get("email") or "").strip().lower()
        name = (decoded_firebase_user.get("name") or payload.get("name") or "Google User").strip()
        if not name:
            name = (decoded_firebase_user.get("firebase", {}).get("sign_in_provider") or "Google User")
        photo_url = (decoded_firebase_user.get("picture") or payload.get("photoURL") or payload.get("picture") or "").strip()
        provider_uid = decoded_firebase_user.get("uid") or payload.get("uid") or email or secrets.token_hex(8)

        user_payload = {
            "uid": f"google-{provider_uid}",
            "name": name,
            "email": email,
            "provider": "google",
            "photoURL": photo_url,
        }

        result = create_or_update_user(user_payload)
        if isinstance(result, tuple):
            response_obj, status_code = result
            return response_obj, status_code
        return result

    @api.route("/auth/google/callback", methods=["GET"])
    def google_auth_callback():
        error = request.args.get("error")
        if error:
            return jsonify({"status": "error", "message": f"Google auth failed: {error}"}), 400

        code = (request.args.get("code") or "").strip()
        if not code:
            return jsonify({"status": "error", "message": "Missing authorization code from Google callback."}), 400

        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": (
                            "Google auth credentials are not configured. "
                            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend .env."
                        ),
                    }
                ),
                501,
            )

        try:
            token_response = _exchange_google_code(code)
            access_token = token_response.get("access_token")
            if not access_token:
                raise RuntimeError("Failed to obtain access token from Google")

            user_info = _fetch_google_user_info(access_token)
            email = (user_info.get("email") or "").strip().lower()
            name = (user_info.get("name") or user_info.get("given_name") or "Google User").strip()
            picture = (user_info.get("picture") or "").strip()

            if not email:
                return (
                    jsonify(
                        {"status": "error", "message": "Google account did not return an email address."}
                    ),
                    400,
                )

            user_payload = {
                "uid": f"google-{email}",
                "name": name,
                "email": email,
                "provider": "google",
                "photoURL": picture,
            }

            create_response = create_or_update_user(user_payload)
            if isinstance(create_response, tuple):
                response_obj, status_code = create_response
            else:
                response_obj = create_response
                status_code = 200

            if status_code != 200 and status_code != 201:
                return create_response

            response_json = json.loads(response_obj.get_data(as_text=True))
            token = response_json.get("token")
            user = response_json.get("user") or {}
            callback_url = _build_frontend_callback_url(token, user)
            return redirect(callback_url)
        except Exception as exc:
            logging.exception("Google callback error")
            return (
                jsonify({"status": "error", "message": f"Google callback failed: {exc}"}),
                502,
            )

    @api.route("/auth/register", methods=["POST"])
    def register_user():
        payload = request.get_json(silent=True) or {}
        return create_or_update_user(payload)

    app.register_blueprint(api)
