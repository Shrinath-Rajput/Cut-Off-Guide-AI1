from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import secrets
import re
import logging
import os
import json
import urllib.parse
import urllib.request
from fastapi.responses import RedirectResponse
from fastapi import Request

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.deps import get_current_user
from app.schemas.user import UserLogin, UserSignup, UserResponse, LoginOtpRequest, LoginOtpVerifyRequest
from app.services.auth_service import normalize_phone, send_otp_sms, verify_otp_sms
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

class OtpRequest(BaseModel):
    name: str
    email: str
    phone: str

class OtpVerifyRequest(OtpRequest):
    otp: str
    sessionId: str
    registerPayload: Optional[dict] = None

_in_memory_users = {}

async def create_or_update_user(payload: UserLogin, db):
    uid = payload.uid

    raw_email = payload.email or ""
    raw_phone = payload.phone or ""

    email = raw_email.strip().lower() if raw_email else ""
    try:
        phone = normalize_phone(raw_phone) if raw_phone else ""
    except Exception:
        phone = raw_phone

    if not uid:
        if phone:
            uid = f"{payload.provider}-{phone}"
        elif email:
            uid = f"{payload.provider}-{email}"
        else:
            uid = f"{payload.provider}-{secrets.token_hex(6)}"

    now = datetime.now(timezone.utc)

    if db is not None:
        try:
            collection = db["users"]
            filter_query = {"uid": uid}
            or_conditions = [{"uid": uid}]
            if email:
                or_conditions.append({"email": email})
            if phone:
                or_conditions.append({"phone": phone})
            filter_query = {"$or": or_conditions}

            existing_user = await collection.find_one(filter_query)

            if existing_user:
                if existing_user.get("role") == "ADMIN":
                    raise HTTPException(status_code=403, detail="Use the admin login")
                update_data = {
                    "name": payload.name or existing_user.get("name", "User"),
                    "provider": payload.provider or existing_user.get("provider", "phone"),
                    "photoURL": payload.photoURL or existing_user.get("photoURL", ""),
                    "lastLogin": now,
                }
                if email and not existing_user.get("email"):
                    update_data["email"] = email
                if phone and not existing_user.get("phone"):
                    update_data["phone"] = phone
                await collection.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": update_data}
                )
                updated_user = await collection.find_one({"_id": existing_user["_id"]})
                updated_user["id"] = str(updated_user["_id"])
                del updated_user["_id"]

                token = create_access_token(subject=existing_user["uid"], role=updated_user.get("role", "USER"))
                return {
                    "status": "success",
                    "message": "User authenticated",
                    "token": token,
                    "user": updated_user
                }

            new_user = {
                "uid": uid,
                "name": payload.name or "User",
                "email": email or None,
                "phone": phone or None,
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
        except HTTPException:
            raise
        except Exception:
            logger.exception("create_or_update_user DB path exception, falling back to memory")

    user_obj = _in_memory_users.get(uid, {
        "id": uid,
        "uid": uid,
        "name": payload.name or "User",
        "email": payload.email or "",
        "phone": payload.phone or "",
        "provider": payload.provider or "phone",
        "photoURL": payload.photoURL or "",
        "role": "USER",
        "createdAt": now.isoformat(),
        "lastLogin": now.isoformat()
    })
    user_obj["lastLogin"] = now.isoformat()
    _in_memory_users[uid] = user_obj
    token = create_access_token(subject=uid, role="USER")
    return {
        "status": "success",
        "message": "User authenticated",
        "token": token,
        "user": user_obj
    }


@router.post("/send-otp")
async def send_otp(request: OtpRequest, db=Depends(get_db)):
    from fastapi.responses import JSONResponse
    try:
        result = await send_otp_sms(request.phone, db)
        response_data = {"status": "success", "message": "OTP sent successfully", "sessionId": result["session_id"]}
        if result.get("provider_request_id"):
            response_data["provider_request_id"] = result["provider_request_id"]
        return response_data
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})

@router.post("/verify-otp")
async def verify_otp(request: OtpVerifyRequest, db=Depends(get_db)):
    from fastapi.responses import JSONResponse
    try:
        is_valid = await verify_otp_sms(request.phone, request.otp, request.sessionId, db)
        if not is_valid:
            raise HTTPException(status_code=400, detail="OTP is invalid or expired")

        normalized_email = request.email.strip().lower() if request.email else ""
        try:
            normalized_phone = normalize_phone(request.phone) if request.phone else ""
        except Exception:
            normalized_phone = request.phone

        query_conditions = []
        if normalized_email:
            query_conditions.append({"email": normalized_email})
        if normalized_phone:
            query_conditions.append({"phone": normalized_phone})

        user = None
        if query_conditions:
            user = await db["users"].find_one({"$or": query_conditions})

        if user is None and normalized_phone:
            all_users = await db["users"].find({}).to_list(length=10000)
            for u in all_users:
                u_phone = u.get("phone")
                if u_phone and isinstance(u_phone, str):
                    try:
                        u_norm = normalize_phone(u_phone)
                        if u_norm == normalized_phone:
                            user = u
                            break
                    except Exception:
                        continue

        if not user and request.registerPayload:
            payload = request.registerPayload
            raw_name = str(payload.get("name") or payload.get("fullName") or request.name or "User").strip()
            raw_email = str(payload.get("email") or normalized_email or request.email or "").strip().lower()
            raw_phone = str(payload.get("phone") or normalized_phone or request.phone or "")
            raw_password = payload.get("password")
            try:
                raw_phone = normalize_phone(raw_phone)
            except HTTPException:
                raise
            except Exception:
                pass

            if not raw_password:
                raise HTTPException(status_code=422, detail="Password is required for new account signup")

            all_users = await db["users"].find({}).to_list(length=10000)

            def _has_password_hash(u):
                ph = u.get("passwordHash") or u.get("password_hash")
                return bool(ph)

            email_dup_matches = []
            for u in all_users:
                u_email = u.get("email")
                if u_email and isinstance(u_email, str) and u_email.strip().lower() == raw_email:
                    email_dup_matches.append(u)

            phone_dup_matches = []
            for u in all_users:
                u_phone = u.get("phone")
                if u_phone and isinstance(u_phone, str):
                    try:
                        if normalize_phone(u_phone) == raw_phone:
                            phone_dup_matches.append(u)
                    except Exception:
                        pass

            email_passworded = [u for u in email_dup_matches if _has_password_hash(u)]
            phone_passworded = [u for u in phone_dup_matches if _has_password_hash(u)]

            if email_passworded:
                logger.warning(
                    "VERIFY-OTP SIGNUP 409: Email already has passwordHash. email=%s existing_uid=%s",
                    raw_email, email_passworded[0].get("uid")
                )
                raise HTTPException(status_code=409, detail="Email already registered. Please sign in instead.")

            if phone_passworded:
                logger.warning(
                    "VERIFY-OTP SIGNUP 409: Phone already has passwordHash. phone=%s existing_uid=%s",
                    raw_phone, phone_passworded[0].get("uid")
                )
                raise HTTPException(status_code=409, detail="Phone number already registered. Please sign in instead.")

            uid = f"user-{secrets.token_hex(12)}"
            password_hash = get_password_hash(raw_password)
            now = datetime.now(timezone.utc)

            new_user = {
                "uid": uid,
                "name": raw_name,
                "email": raw_email or None,
                "phone": raw_phone or None,
                "provider": "password",
                "role": "USER",
                "passwordHash": password_hash,
                "userType": payload.get("userType") or "student",
                "createdAt": now,
                "lastLogin": now,
            }
            try:
                result = await db["users"].insert_one(new_user)
            except Exception as insert_err:
                logger.exception("verify-otp signup: users insert_one FAILED: %s", insert_err)
                err_str = str(insert_err).lower()
                if "duplicate" in err_str or "e11000" in err_str:
                    if "email" in err_str:
                        raise HTTPException(status_code=409, detail="Email already registered. Please sign in instead.")
                    if "phone" in err_str:
                        raise HTTPException(status_code=409, detail="Phone number already registered. Please sign in instead.")
                    raise HTTPException(status_code=409, detail="Account with this information already exists. Please sign in.")
                raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

            profile_dict = {}
            for k, v in payload.items():
                if k in ("password", "_id"):
                    continue
                profile_dict[k] = v
            profile_dict.update({
                "uid": uid,
                "name": raw_name,
                "email": raw_email,
                "phone": raw_phone,
                "createdAt": now,
                "updatedAt": now,
            })
            try:
                await db["profiles"].insert_one(profile_dict)
            except Exception as profile_err:
                logger.exception("verify-otp signup: profile insert FAILED (rolling back user): %s", profile_err)
                try:
                    await db["users"].delete_one({"uid": uid})
                except Exception:
                    pass
                raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

            user = new_user
            user["id"] = str(result.inserted_id)
            user.pop("passwordHash", None)
            user.pop("password_hash", None)
            token = create_access_token(subject=uid, role="USER")
            return {
                "status": "success",
                "message": "Account created and verified successfully",
                "token": token,
                "user": user,
                "newAccount": True,
            }

        if not user:
            raise HTTPException(status_code=401, detail="Account not found. Please sign up first.")
        token = create_access_token(subject=user["uid"], role=user.get("role", "USER"))
        user["id"] = str(user.pop("_id"))
        user.pop("passwordHash", None)
        user.pop("password_hash", None)
        return {"status": "success", "message": "Authentication successful", "token": token, "user": user}
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/register")
async def register(request: UserSignup, db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    raw_email = request.email
    raw_phone = request.phone
    raw_name = request.name
    raw_password = request.password

    email = raw_email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")

    try:
        phone = normalize_phone(raw_phone)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=422, detail="Enter a valid 10-digit phone number")

    password_present = raw_password is not None and raw_password != ""
    password_length = len(raw_password) if raw_password else 0

    logger.info(
        "REGISTER called: raw_email=%s raw_phone=%s -> normalized email=%s phone=%s. "
        "Password present=%s, password length=%d. NEVER logging actual password.",
        repr(raw_email), repr(raw_phone), repr(email), repr(phone),
        password_present, password_length
    )

    if not password_present or password_length < 1:
        raise HTTPException(status_code=422, detail="Password is required")

    all_users = await db["users"].find({}).to_list(length=10000)

    def _has_password_hash(u):
        ph = u.get("passwordHash") or u.get("password_hash")
        return bool(ph)

    email_matches = []
    for u in all_users:
        u_email = u.get("email")
        if u_email and isinstance(u_email, str) and u_email.strip().lower() == email:
            email_matches.append(u)

    phone_matches = []
    for u in all_users:
        u_phone = u.get("phone")
        if u_phone and isinstance(u_phone, str):
            try:
                if normalize_phone(u_phone) == phone:
                    phone_matches.append(u)
            except Exception:
                pass

    logger.info(
        "REGISTER duplicate scan complete: email_matches=%d (passworded=%d), phone_matches=%d (passworded=%d)",
        len(email_matches), sum(1 for u in email_matches if _has_password_hash(u)),
        len(phone_matches), sum(1 for u in phone_matches if _has_password_hash(u))
    )

    def _score_user_for_update(u, for_email):
        score = 0
        if for_email:
            if u.get("email") and u.get("email").strip().lower() == email:
                score += 1000
            if u.get("phone"):
                try:
                    if normalize_phone(u.get("phone")) == phone:
                        score += 500
                except Exception:
                    pass
        else:
            if u.get("phone"):
                try:
                    if normalize_phone(u.get("phone")) == phone:
                        score += 1000
                except Exception:
                    pass
            if u.get("email") and u.get("email").strip().lower() == email:
                score += 500
        if bool(u.get("lastLogin")):
            score += 50
        if u.get("provider") == "phone":
            score += 10
        return score

    email_passworded = [u for u in email_matches if _has_password_hash(u)]
    email_unpassworded = [u for u in email_matches if not _has_password_hash(u)]
    phone_passworded = [u for u in phone_matches if _has_password_hash(u)]
    phone_unpassworded = [u for u in phone_matches if not _has_password_hash(u)]

    chosen_user_to_update = None
    update_reason = None

    if email_passworded:
        eu = email_passworded[0]
        logger.warning(
            "REGISTER 409: Email already registered AND HAS passwordHash. email=%s existing_uid=%s stored_email=%s",
            email, eu.get("uid"), repr(eu.get("email"))
        )
        raise HTTPException(status_code=409, detail="Email already registered")

    if phone_passworded:
        pu = phone_passworded[0]
        logger.warning(
            "REGISTER 409: Phone already registered AND HAS passwordHash. phone=%s existing_uid=%s stored_phone=%s",
            phone, pu.get("uid"), repr(pu.get("phone"))
        )
        raise HTTPException(status_code=409, detail="Phone number already registered")

    if email_unpassworded:
        candidates = sorted(email_unpassworded, key=lambda u: _score_user_for_update(u, for_email=True), reverse=True)
        chosen_user_to_update = candidates[0]
        update_reason = "email_existing_no_passwordHash"
        logger.info(
            "REGISTER UPDATE PATH (email): Found existing user uid=%s WITHOUT passwordHash. Will UPDATE with password + profile instead of 409. provider=%s stored_email=%s stored_phone=%s",
            chosen_user_to_update.get("uid"),
            chosen_user_to_update.get("provider"),
            repr(chosen_user_to_update.get("email")),
            repr(chosen_user_to_update.get("phone"))
        )
        # Check if this chosen user's phone ALSO doesn't conflict with any passworded user (already done above since phone_passworded was empty).
        # But check: is there ANOTHER phone-unpassworded user that is DIFFERENT from this chosen one? If so, that's ok - we only update the best-match (email) one.
        if not chosen_user_to_update.get("phone"):
            # Check if another UNPASSWORD user exists with this phone. Ensure we don't create 2 updated-with-password accounts.
            other_phone_owned = [u for u in phone_unpassworded if str(u.get("_id")) != str(chosen_user_to_update.get("_id"))]
            if other_phone_owned:
                logger.info(
                    "REGISTER UPDATE PATH (email): Note phone=%s is owned by another unpassworded user uid=%s (not updating that one).",
                    phone, other_phone_owned[0].get("uid")
                )
    elif phone_unpassworded:
        candidates = sorted(phone_unpassworded, key=lambda u: _score_user_for_update(u, for_email=False), reverse=True)
        chosen_user_to_update = candidates[0]
        update_reason = "phone_existing_no_passwordHash"
        logger.info(
            "REGISTER UPDATE PATH (phone): Found existing user uid=%s WITHOUT passwordHash. Will UPDATE with password + profile instead of 409. provider=%s stored_email=%s stored_phone=%s",
            chosen_user_to_update.get("uid"),
            chosen_user_to_update.get("provider"),
            repr(chosen_user_to_update.get("email")),
            repr(chosen_user_to_update.get("phone"))
        )

    now = datetime.now(timezone.utc)

    if chosen_user_to_update is not None:
        existing_uid = chosen_user_to_update.get("uid")
        existing_id = chosen_user_to_update.get("_id")

        logger.info(
            "REGISTER UPDATE: Hashing password for existing uid=%s (length=%d). NEVER logging hash or password.",
            existing_uid, password_length
        )
        password_hash = get_password_hash(raw_password)

        user_update_set = {
            "passwordHash": password_hash,
            "provider": "password",
            "name": raw_name.strip(),
            "lastLogin": now,
        }
        if not chosen_user_to_update.get("email"):
            user_update_set["email"] = email
        if not chosen_user_to_update.get("phone"):
            user_update_set["phone"] = phone

        try:
            await db["users"].update_one(
                {"_id": existing_id},
                {"$set": user_update_set}
            )
            logger.info(
                "REGISTER UPDATE: users updated ok uid=%s updated_fields=%s",
                existing_uid, sorted(user_update_set.keys())
            )
        except Exception as up_err:
            logger.exception("REGISTER UPDATE: MongoDB update_one(user) FAILED: %s", up_err)
            raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

        profile = request.model_dump(exclude={"password"})
        profile.update({
            "uid": existing_uid,
            "name": raw_name.strip(),
            "email": email,
            "phone": phone,
            "updatedAt": now,
        })
        try:
            existing_profile = await db["profiles"].find_one({"uid": existing_uid})
            if existing_profile:
                profile["createdAt"] = existing_profile.get("createdAt") or now
                await db["profiles"].update_one({"uid": existing_uid}, {"$set": profile})
                logger.info("REGISTER UPDATE: profiles updated ok uid=%s (reason=%s)", existing_uid, update_reason)
            else:
                profile["createdAt"] = now
                await db["profiles"].insert_one(profile)
                logger.info("REGISTER UPDATE: profiles inserted ok uid=%s (reason=%s)", existing_uid, update_reason)
        except Exception as prof_err:
            logger.exception("REGISTER UPDATE: profile persist FAILED (rollback passwordHash): %s", prof_err)
            try:
                await db["users"].update_one(
                    {"_id": existing_id},
                    {"$unset": {"passwordHash": "", "password_hash": ""},
                     "$set": {"provider": chosen_user_to_update.get("provider")}}
                )
                logger.warning("REGISTER UPDATE: Rolled back passwordHash on user uid=%s due to profile failure", existing_uid)
            except Exception:
                logger.exception("REGISTER UPDATE: Failed to rollback passwordHash on uid=%s", existing_uid)
            raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

        updated_user = await db["users"].find_one({"_id": existing_id})
        updated_user["id"] = str(updated_user.pop("_id"))
        updated_user.pop("passwordHash", None)
        updated_user.pop("password_hash", None)
        logger.info("REGISTER UPDATE SUCCESS: uid=%s email=%s phone=%s (reason=%s)", existing_uid, email, phone, update_reason)
        return {
            "status": "success",
            "message": "Account setup complete. Please sign in with your new password.",
            "user": updated_user,
        }

    uid = f"user-{secrets.token_hex(12)}"
    password_hash = get_password_hash(raw_password)
    logger.info(
        "REGISTER: Creating NEW user uid=%s name=%s email=%s phone=%s provider=password",
        uid, repr(raw_name.strip()), email, phone
    )

    user = {
        "uid": uid,
        "name": raw_name.strip(),
        "email": email,
        "phone": phone,
        "provider": "password",
        "role": "USER",
        "passwordHash": password_hash,
        "createdAt": now,
        "lastLogin": now,
    }
    try:
        result = await db["users"].insert_one(user)
    except Exception as insert_err:
        logger.exception("REGISTER: MongoDB insert_one(user) FAILED: %s", insert_err)
        if "duplicate" in str(insert_err).lower() or "E11000" in str(insert_err):
            if "email" in str(insert_err).lower():
                raise HTTPException(status_code=409, detail="Email already registered")
            if "phone" in str(insert_err).lower():
                raise HTTPException(status_code=409, detail="Phone number already registered")
            raise HTTPException(status_code=409, detail="Account with this information already exists")
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

    try:
        profile = request.model_dump(exclude={"password"})
        profile.update({"uid": uid, "name": user["name"], "email": email, "phone": phone, "createdAt": now, "updatedAt": now})
        await db["profiles"].insert_one(profile)
    except Exception as profile_err:
        logger.exception("REGISTER: MongoDB insert_one(profile) FAILED: %s", profile_err)
        try:
            await db["users"].delete_one({"uid": uid})
            logger.warning("REGISTER: Rolled back user uid=%s due to profile insert failure", uid)
        except Exception:
            logger.exception("REGISTER: Failed to roll back user uid=%s", uid)
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

    logger.info("REGISTER SUCCESS: uid=%s email=%s phone=%s", uid, email, phone)
    user["id"] = str(result.inserted_id)
    user.pop("_id", None)
    user.pop("passwordHash", None)
    return {"status": "success", "message": "Account created successfully. Please sign in.", "user": user}

@router.post("/login")
async def login(request: UserLogin, db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database is unavailable")

    raw_identifier = (request.username or request.email or "").strip()
    identifier = raw_identifier.lower()
    password = (request.password or "").strip()

    if not identifier or not password:
        raise HTTPException(status_code=422, detail="Username/email and password are required")

    try:
        normalized_phone = normalize_phone(raw_identifier)
        is_phone_lookup = True
    except Exception:
        normalized_phone = None
        is_phone_lookup = False

    logger.info(
        "LOGIN called: raw_identifier=%s identifier=%s is_phone=%s phone_norm=%s",
        repr(raw_identifier), repr(identifier), is_phone_lookup, repr(normalized_phone)
    )

    query_conditions = [
        {"email": identifier},
        {"email": raw_identifier},
        {"uid": identifier},
        {"uid": raw_identifier},
        {"username": identifier},
        {"username": raw_identifier},
    ]
    if is_phone_lookup and normalized_phone:
        query_conditions.append({"phone": normalized_phone})
        try:
            all_users = await db["users"].find({}).to_list(length=10000)
            for u in all_users:
                u_phone = u.get("phone")
                if u_phone and isinstance(u_phone, str):
                    try:
                        u_norm = normalize_phone(u_phone)
                        if u_norm == normalized_phone:
                            user_via_scan = u
                            break
                    except Exception:
                        continue
            else:
                user_via_scan = None
        except Exception:
            user_via_scan = None
    else:
        user_via_scan = None

    user = await db["users"].find_one({"$or": query_conditions})
    if user is None and user_via_scan is not None:
        logger.info(
            "LOGIN: Found user via phone-scan (non-normalized DB record) uid=%s stored_phone=%s",
            user_via_scan.get("uid"), repr(user_via_scan.get("phone"))
        )
        user = user_via_scan

    if user is None:
        logger.warning("LOGIN FAILED: No user found for identifier=%s", identifier)
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    stored_password_hash = user.get("passwordHash") or user.get("password_hash")
    legacy_plain_or_hash = user.get("password")
    logger.info(
        "LOGIN: user found uid=%s email=%s phone=%s provider=%s has_passwordHash=%s legacy_password_field=%s",
        user.get("uid"),
        repr(user.get("email")),
        repr(user.get("phone")),
        user.get("provider"),
        bool(stored_password_hash),
        isinstance(legacy_plain_or_hash, str)
    )

    password_valid = False
    if stored_password_hash:
        try:
            password_valid = verify_password(password, stored_password_hash)
        except Exception as verify_err:
            logger.exception("LOGIN: password verification exception for hash field: %s", verify_err)
            password_valid = False

    if not password_valid and isinstance(legacy_plain_or_hash, str) and legacy_plain_or_hash.strip():
        try:
            legacy_value = legacy_plain_or_hash.strip()
            if verify_password(password, legacy_value):
                password_valid = True
            elif password == legacy_value:
                password_valid = True
        except Exception as legacy_err:
            logger.exception("LOGIN: legacy password field verification failed uid=%s: %s", user.get("uid"), legacy_err)
            password_valid = False

        if password_valid and not stored_password_hash:
            try:
                migrated_hash = get_password_hash(password)
                await db["users"].update_one(
                    {"_id": user["_id"]},
                    {"$set": {"passwordHash": migrated_hash, "provider": user.get("provider") or "password"}, "$unset": {"password": ""}}
                )
                logger.info("LOGIN migrated legacy password for uid=%s into passwordHash", user.get("uid"))
            except Exception as migrate_err:
                logger.exception("LOGIN: failed to migrate legacy password hash for uid=%s: %s", user.get("uid"), migrate_err)

    if not stored_password_hash and not isinstance(legacy_plain_or_hash, str):
        logger.warning(
            "LOGIN FAILED: Account uid=%s has NO passwordHash and NO legacy password field. Provider=%s.",
            user.get("uid"), user.get("provider")
        )
        raise HTTPException(
            status_code=401,
            detail="This account was created using Phone OTP or Google Sign-In and does not have a password set. "
                   "Please use Phone Number OTP login, or contact support to set a password."
        )

    logger.info(
        "LOGIN credential check uid=%s password_valid=%s",
        user.get("uid"), password_valid
    )

    if not password_valid:
        logger.warning("LOGIN FAILED: Incorrect password for uid=%s identifier=%s", user.get("uid"), identifier)
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    user["id"] = str(user.pop("_id"))
    user.pop("passwordHash", None)
    user.pop("password_hash", None)
    user.pop("password", None)
    if user.get("role") == "ADMIN":
        return {
            "status": "success",
            "message": "Admin authenticated",
            "token": create_access_token(user["uid"], role="ADMIN"),
            "user": user,
        }

    logger.info("LOGIN SUCCESS: uid=%s. Proceeding to OTP stage.", user.get("uid"))
    return {
        "status": "success",
        "message": "Credentials verified",
        "requiresOtp": True,
        "user": user,
        "otpPhone": user.get("phone"),
        "uid": user["uid"]
    }

@router.post("/login/send-otp")
async def send_login_otp(request: LoginOtpRequest, db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="OTP service is currently unavailable")

    requested_phone = normalize_phone(request.phone)
    user = await db["users"].find_one({"uid": request.uid})
    if not user:
        raise HTTPException(status_code=401, detail="User account was not found")

    registered_phone = user.get("phone")
    if not registered_phone:
        raise HTTPException(status_code=400, detail="Phone number is not registered for this account")
    if normalize_phone(registered_phone) != requested_phone:
        raise HTTPException(status_code=400, detail="Phone number does not match this account")

    result = await send_otp_sms(registered_phone, db)
    return {"status": "success", "message": "OTP sent successfully", "sessionId": result["session_id"]}

@router.post("/login/verify-otp")
async def verify_login_otp(request: LoginOtpVerifyRequest, db=Depends(get_db)):
    if not await verify_otp_sms(request.phone, request.otp, request.sessionId, db):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    user = await db["users"].find_one({"uid": request.uid})
    if not user:
        raise HTTPException(status_code=401, detail="User account was not found")
    if not user.get("phone"):
        raise HTTPException(status_code=400, detail="Phone number is not registered for this account")
    if normalize_phone(user["phone"]) != normalize_phone(request.phone):
        raise HTTPException(status_code=400, detail="Phone number does not match this account")
    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"lastLogin": datetime.now(timezone.utc)}})
    user["id"] = str(user.pop("_id"))
    user.pop("passwordHash", None)
    return {"status": "success", "token": create_access_token(user["uid"], role=user.get("role", "USER")), "user": user}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    user = dict(current_user)
    user.pop("passwordHash", None)
    user.pop("password_hash", None)
    return {
        "status": "success",
        "user": user
    }

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv(
    "GOOGLE_OAUTH_REDIRECT_URI",
    "http://localhost:5000/api/auth/google/callback",
)
FRONTEND_APP_URL = os.getenv("FRONTEND_APP_URL", "http://localhost:5173")

def _build_google_auth_url():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

def _exchange_google_code(code):
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_OAUTH_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    request_obj = urllib.request.Request(token_url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request_obj, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

def _fetch_google_user_info(access_token):
    request_obj = urllib.request.Request(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urllib.request.urlopen(request_obj, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

def _build_frontend_callback_url(token, user):
    query = urllib.parse.urlencode(
        {
            "token": token,
            "uid": user.get("uid", ""),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "photoURL": user.get("photoURL", ""),
        }
    )
    return f"{FRONTEND_APP_URL}/auth/google/callback?{query}"

@router.get("/google")
async def google_auth():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=501, 
            detail="Google OAuth credentials are not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend .env."
        )
    return RedirectResponse(url=_build_google_auth_url())

@router.get("/google/callback")
async def google_auth_callback(request: Request, db=Depends(get_db)):
    error = request.query_params.get("error")
    if error:
        raise HTTPException(status_code=400, detail=f"Google auth failed: {error}")

    code = (request.query_params.get("code") or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Google callback.")

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=501, 
            detail="Google auth credentials are not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend .env."
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
            raise HTTPException(status_code=400, detail="Google account did not return an email address.")

        user_payload = UserLogin(
            uid=f"google-{email}",
            name=name,
            email=email,
            provider="google",
            photoURL=picture,
        )

        create_response = await create_or_update_user(user_payload, db)
        
        token = create_response.get("token")
        user = create_response.get("user") or {}
        callback_url = _build_frontend_callback_url(token, user)
        return RedirectResponse(url=callback_url)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Google callback error")
        raise HTTPException(status_code=502, detail=f"Google callback failed: {exc}")
