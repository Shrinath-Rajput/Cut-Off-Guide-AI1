"""Complete password persistence test suite - ALL 7 TESTS
   Tests:
   TEST 1: New email + new phone + password -> 200, DB has passwordHash
   TEST 2: Login TEST 1 user CORRECT password -> 200, OTP stage
   TEST 3: Login TEST 1 user WRONG password -> 401
   TEST 4: Register existing rajputshrinath349@gmail.com + password -> UPDATE existing user (no 409), passwordHash NOW present
   TEST 5: Login rajputshrinath349@gmail.com + same password -> 200, OTP stage (NO legacy error)
   TEST 6: OTP verification (mock/live depending on mode)
   TEST 7: Profile page for that user returns correct onboarding data
"""
import os
import re
import sys
import json
import secrets
import asyncio
from pathlib import Path

import requests

BASE = "http://127.0.0.1:5000"

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / ".venv" / "Lib" / "site-packages"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.auth_service import normalize_phone
from app.core.security import verify_password


def make_request(method, path, **kwargs):
    url = BASE + path
    # Redact password in logs
    redacted_kwargs = json.loads(json.dumps(kwargs, default=str))
    if "json" in redacted_kwargs and isinstance(redacted_kwargs["json"], dict):
        for k in ["password", "passwordHash", "password_hash"]:
            if k in redacted_kwargs["json"]:
                redacted_kwargs["json"][k] = "***REDACTED***"
    print("=" * 80)
    print(f"REQUEST: {method} {path}")
    if redacted_kwargs.get("json"):
        print(f"  Payload: {json.dumps(redacted_kwargs['json'], indent=2)}")
    try:
        resp = requests.request(method, url, timeout=30, **kwargs)
    except Exception as e:
        print(f"  EXCEPTION during HTTP: {e}")
        raise
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    print(f"  Status: {resp.status_code}")
    if isinstance(body, dict):
        safe_body = json.loads(json.dumps(body))
        for k in ["password", "passwordHash", "password_hash", "access_token", "token"]:
            if k in safe_body and isinstance(safe_body[k], str):
                val = safe_body[k]
                safe_body[k] = val[:4] + "*" * max(0, len(val) - 8) + val[-4:] if len(val) > 8 else "***REDACTED***"
        print(f"  Response: {json.dumps(safe_body, indent=2)}")
    else:
        print(f"  Response: {body}")
    return resp


async def check_db_has_password(email):
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    try:
        users = []
        async for u in db["users"].find({}):
            ue = u.get("email")
            if ue and isinstance(ue, str) and ue.strip().lower() == email.strip().lower():
                users.append(u)
        if not users:
            # try phone if it matches
            print(f"    [DB] No user found by email {email!r}.")
            return False, None
        # pick the most recently logged in / updated
        best = sorted(users, key=lambda u: (u.get("lastLogin") or u.get("createdAt")), reverse=True)[0]
        ph = best.get("passwordHash") or best.get("password_hash")
        has = bool(ph)
        print(f"    [DB] Found user uid={best.get('uid')} provider={best.get('provider')} has_passwordHash={has} _id={best.get('_id')}")
        if has:
            print(f"    [DB] passwordHash field PRESENT in doc: {('passwordHash' in best) or ('password_hash' in best)}")
        client.close()
        return has, best


async def verify_password_in_db(email, submitted_password):
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    try:
        found = None
        async for u in db["users"].find({}):
            ue = u.get("email")
            if ue and isinstance(ue, str) and ue.strip().lower() == email.strip().lower():
                if (u.get("passwordHash") or u.get("password_hash")):
                    found = u
                    break
        if not found:
            print(f"    [VERIFY] No passworded user found for {email}.")
            return False
        stored = found.get("passwordHash") or found.get("password_hash")
        ok = verify_password(submitted_password, stored)
        print(f"    [VERIFY] verify_password({email}, submitted_pw) -> {ok}")
        client.close()
        return ok


async def get_profile_for_uid(uid):
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    try:
        return await db["profiles"].find_one({"uid": uid})
    finally:
        await client.close()


async def run_tests():
    numeric = "".join(str(ord(c) % 10) for c in secrets.token_hex(5))[:12]
    tag = secrets.token_hex(5)
    print("=" * 80)
    print(f"PASSWORD PERSISTENCE TEST SUITE - tag={tag}")
    print("=" * 80)

    resp = make_request("GET", "/api/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    assert resp.json().get("status") == "ok"

    NEW_EMAIL = f"newuser-{tag}@example.com"
    NEW_PHONE = f"7{numeric[:9]}"
    NEW_PASSWORD = "FreshPass@2026"
    if len(NEW_PHONE) < 10:
        NEW_PHONE = NEW_PHONE + "0" * (10 - len(NEW_PHONE))

    LEGACY_EMAIL = "rajputshrinath349@gmail.com"
    LEGACY_PHONE = "9699510445"
    LEGACY_PASSWORD = "LegacyPass@2026"

    print("\n" + "#" * 80)
    print("PRE-TEST SANITY: Confirm legacy account has NO passwordHash currently")
    print("#" * 80)
    has_before, legacy_before = await check_db_has_password(LEGACY_EMAIL)
    assert legacy_before is not None, f"Legacy user {LEGACY_EMAIL} not in DB - cannot run TEST 4/5"
    print(f"  Pre-check: {LEGACY_EMAIL} has_passwordHash={has_before} (expected: NO before we update)")

    # ---------- TEST 1 ----------
    print("\n" + "#" * 80)
    print("TEST 1: Register COMPLETELY NEW email + NEW phone + password")
    print(f"         email={NEW_EMAIL}  phone={NEW_PHONE}")
    print("#" * 80)
    payload = {
        "name": "Brand New User",
        "email": NEW_EMAIL,
        "phone": NEW_PHONE,
        "password": NEW_PASSWORD,
        "category": "OBC",
        "pwdCrossCategory": True,
        "domicile": "Karnataka",
        "exam": "JEE Main",
        "examScore": "92",
        "careerOption": "Engineering",
        "preferredBranch": "Information Technology",
        "preferredLocation": "Bengaluru",
        "budgetRange": "10",
        "collegeType": "Private",
        "hostelRequired": False,
    }
    resp = make_request("POST", "/api/auth/register", json=payload)
    assert resp.status_code == 200, f"TEST 1 FAILED: Expected 200, got {resp.status_code}. Body: {resp.text}"
    data = resp.json()
    assert data.get("status") == "success", f"TEST 1 FAILED: status != success: {data}"
    user_obj = data.get("user")
    assert user_obj, f"TEST 1 FAILED: user object missing"
    assert user_obj.get("email") == NEW_EMAIL, f"TEST 1 FAILED: returned email mismatch"
    print("  [PASS] TEST 1 HTTP level: New user register returned success")
    has_pw, db_user = await check_db_has_password(NEW_EMAIL)
    assert has_pw is True, "TEST 1 FAILED DB: passwordHash is missing after register!"
    assert db_user.get("provider") == "password", f"TEST 1 FAILED DB: provider should be password, got {db_user.get('provider')}"
    ok_verify = await verify_password_in_db(NEW_EMAIL, NEW_PASSWORD)
    assert ok_verify is True, "TEST 1 FAILED DB: verify_password did not match submitted password against stored passwordHash!"
    print("  [PASS] TEST 1 DB level: passwordHash present + verify_password MATCHES submitted password")

    # ---------- TEST 2 ----------
    print("\n" + "#" * 80)
    print("TEST 2: Login TEST 1 user with CORRECT password -> should proceed to OTP stage")
    print("#" * 80)
    resp = make_request("POST", "/api/auth/login", json={"username": NEW_EMAIL, "password": NEW_PASSWORD})
    assert resp.status_code == 200, f"TEST 2 FAILED: Expected 200, got {resp.status_code}. Body: {resp.text}"
    data = resp.json()
    assert data.get("status") == "success", f"TEST 2 FAILED: status != success: {data}"
    assert data.get("requiresOtp") is True, f"TEST 2 FAILED: requiresOtp should be True, got {data.get('requiresOtp')}"
    assert data.get("otpPhone") == NEW_PHONE, f"TEST 2 FAILED: otpPhone mismatch: {data.get('otpPhone')} != {NEW_PHONE}"
    assert data.get("uid"), "TEST 2 FAILED: uid missing"
    # Also confirm no mention of "Phone OTP or Google" in response (it would have been a legacy-style 401 message - success 200 already proves it)
    print("  [PASS] TEST 2: Login CORRECT password -> 200 + requiresOtp=True + correct otpPhone. OTP-before-session preserved.")

    # ---------- TEST 3 ----------
    print("\n" + "#" * 80)
    print("TEST 3: Login TEST 1 user with WRONG password -> 401")
    print("#" * 80)
    resp = make_request("POST", "/api/auth/login", json={"username": NEW_EMAIL, "password": "AbsolutelyWrong@999"})
    assert resp.status_code == 401, f"TEST 3 FAILED: Expected 401, got {resp.status_code}. Body: {resp.text}"
    detail = resp.json().get("detail", "")
    assert isinstance(detail, str), "TEST 3 FAILED: no detail message"
    assert "Invalid" in detail or "password" in detail.lower() or "username" in detail.lower(), f"TEST 3 FAILED: message doesn't look like invalid creds: {detail}"
    print(f"  [PASS] TEST 3: Wrong password correctly rejected -> 401. Message: {detail}")

    # ---------- TEST 4 ----------
    print("\n" + "#" * 80)
    print("TEST 4: Register with EXISTING legacy email rajputshrinath349@gmail.com")
    print(f"         It currently has NO passwordHash -> UPDATE existing user instead of 409.")
    print("#" * 80)
    payload = {
        "name": "shrinath Rajput",
        "email": LEGACY_EMAIL,
        "phone": LEGACY_PHONE,
        "password": LEGACY_PASSWORD,
        "category": "General",
        "pwdCrossCategory": False,
        "domicile": "Maharashtra",
        "exam": "Diploma",
        "examScore": "90",
        "careerOption": "Engineering",
        "preferredBranch": "Computer Science",
        "preferredLocation": "pune",
        "budgetRange": "0-10",
        "collegeType": "Government",
        "hostelRequired": True,
    }
    resp = make_request("POST", "/api/auth/register", json=payload)
    assert resp.status_code == 200, f"TEST 4 FAILED: Expected 200 (update existing account), got {resp.status_code}. Body: {resp.text}"
    data = resp.json()
    assert data.get("status") == "success", f"TEST 4 FAILED: status != success: {data}"
    updated_user_obj = data.get("user")
    assert updated_user_obj, "TEST 4 FAILED: user object missing"
    returned_uid = updated_user_obj.get("uid")
    before_uid = legacy_before.get("uid")
    print(f"  Info: before-update uid={before_uid}. Register-returned uid={returned_uid}")
    print(f"  Info: before-update _id={legacy_before.get('_id')}. Register returned user.id={updated_user_obj.get('id')}")
    assert returned_uid == before_uid, f"TEST 4 FAILED: User uid should NOT change during update! It was {before_uid}, now {returned_uid}. NEW USER CREATED INSTEAD OF UPDATE."
    assert updated_user_obj.get("id") == str(legacy_before.get("_id")), f"TEST 4 FAILED: User _id should NOT change during update! OLD={legacy_before.get('_id')}, NEW={updated_user_obj.get('id')}"
    print("  [PASS] TEST 4 HTTP level: Returned 200 success. UID and _id MATCH existing user (no new record was created)")

    has_pw_after, legacy_after = await check_db_has_password(LEGACY_EMAIL)
    assert has_pw_after is True, "TEST 4 FAILED DB: passwordHash NOT updated on existing legacy user!"
    assert legacy_after.get("uid") == before_uid, f"TEST 4 FAILED DB: uid changed after update!"
    assert legacy_after.get("_id") == legacy_before.get("_id"), f"TEST 4 FAILED DB: _id changed after update!"
    ok_verify_legacy = await verify_password_in_db(LEGACY_EMAIL, LEGACY_PASSWORD)
    assert ok_verify_legacy is True, "TEST 4 FAILED DB: verify_password on legacy account with submitted LEGACY_PASSWORD failed!"
    print("  [PASS] TEST 4 DB level: Existing user document now has passwordHash. Submitted password verify_password returns True. Same _id preserved.")

    # Also check there is no NEW duplicate user created with this email that is NOT the original
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    try:
        passworded_matches = []
        async for u in db["users"].find({}):
            ue = u.get("email")
            if ue and isinstance(ue, str) and ue.strip().lower() == LEGACY_EMAIL.strip().lower():
                if (u.get("passwordHash") or u.get("password_hash")):
                    passworded_matches.append(u)
        print(f"  [PASS] TEST 4 DB audit: Passworded users with email {LEGACY_EMAIL} = {len(passworded_matches)} (expected 1)")
        assert len(passworded_matches) == 1, f"TEST 4 FAILED DB audit: Expected exactly 1 passworded user for {LEGACY_EMAIL}, found {len(passworded_matches)}: {[u.get('uid') for u in passworded_matches]}"
    finally:
        await client.close()

    # ---------- TEST 5 ----------
    print("\n" + "#" * 80)
    print("TEST 5: Login rajputshrinath349@gmail.com + SAME password used during signup")
    print("         Should return success 200 + proceed to OTP stage. MUST NOT say 'Phone OTP or Google'.")
    print("#" * 80)
    resp = make_request("POST", "/api/auth/login", json={"username": LEGACY_EMAIL, "password": LEGACY_PASSWORD})
    assert resp.status_code == 200, f"TEST 5 FAILED: Expected 200, got {resp.status_code}. Body: {resp.text}"
    data = resp.json()
    assert data.get("status") == "success", f"TEST 5 FAILED: status != success: {data}"
    assert data.get("requiresOtp") is True, f"TEST 5 FAILED: requiresOtp should be True: {data}"
    assert data.get("uid") == before_uid, f"TEST 5 FAILED: uid mismatch: {data.get('uid')} != {before_uid}"
    assert "otpPhone" in data, "TEST 5 FAILED: otpPhone missing in response (should go to OTP stage)"
    detail_text = resp.text.lower()
    assert "phone otp or google" not in detail_text, f"TEST 5 FAILED: Legacy error message present in success response 200 - should not be there!"
    print("  [PASS] TEST 5: Legacy account with newly-set password logs in successfully -> 200 + requiresOtp + OTP stage. NO legacy 'Phone OTP or Google' error.")

    # Quick double-check: WRONG password on legacy account -> 401 (not 200, not legacy)
    resp_wrong = requests.post(BASE + "/api/auth/login", json={"username": LEGACY_EMAIL, "password": "WrongLegacy@999"}, timeout=30)
    assert resp_wrong.status_code == 401, f"TEST 5b FAILED: Wrong password on legacy should be 401, got {resp_wrong.status_code}"
    print(f"  [PASS] TEST 5 extra: Wrong password on legacy -> 401 (correctly rejected)")

    # ---------- TEST 6 ----------
    print("\n" + "#" * 80)
    print("TEST 6: OTP verification flow on TEST 1 user -> session JWT & home redirect payload")
    print("#" * 80)
    login_resp = requests.post(BASE + "/api/auth/login", json={"username": NEW_EMAIL, "password": NEW_PASSWORD}, timeout=30)
    login_data = login_resp.json()
    t6_uid = login_data.get("uid")
    t6_phone = login_data.get("otpPhone")
    assert t6_uid and t6_phone, "TEST 6 setup: Can't do OTP flow - login didn't return uid/otpPhone"

    send_resp = make_request("POST", "/api/auth/login/send-otp", json={"uid": t6_uid, "phone": t6_phone, "name": "Brand New User", "email": NEW_EMAIL})
    assert send_resp.status_code == 200, f"TEST 6 FAILED send-otp: Expected 200, got {send_resp.status_code}. Body: {send_resp.text}"
    send_data = send_resp.json()
    assert send_data.get("status") == "success", f"TEST 6 FAILED send-otp: status != success: {send_data}"
    session_id = send_data.get("sessionId")
    assert session_id, f"TEST 6 FAILED send-otp: sessionId missing"
    print(f"  TEST 6: OTP sent, sessionId present ({len(session_id)} chars)")

    # Now get OTP from MongoDB directly (skip SMS read). Development mode may use static '123456'. Also try to read otps collection.
    dev_otp = "123456"
    actual_otp = dev_otp
    try:
        uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        found_otp = None
        async for o in db["otps"].find({"sessionId": session_id}).sort("createdAt", -1):
            found_otp = o
            break
        if found_otp:
            actual_otp = str(found_otp.get("otp") or dev_otp)
            print(f"  TEST 6: Retrieved actual OTP from MongoDB otps collection (length={len(actual_otp)}).")
        await client.close()
    except Exception as e:
        print(f"  TEST 6: Could not read OTP from DB ({e}); using dev default {actual_otp}")

    verify_body = {
        "uid": t6_uid,
        "phone": t6_phone,
        "otp": actual_otp,
        "sessionId": session_id,
        "name": "Brand New User",
        "email": NEW_EMAIL,
    }
    verify_resp = make_request("POST", "/api/auth/login/verify-otp", json=verify_body)
    assert verify_resp.status_code == 200, f"TEST 6 FAILED verify-otp: Expected 200, got {verify_resp.status_code}. Body: {verify_resp.text}"
    verify_data = verify_resp.json()
    assert verify_data.get("status") == "success", f"TEST 6 FAILED verify-otp: status != success: {verify_data}"
    token = verify_data.get("token") or verify_data.get("access_token")
    assert token and isinstance(token, str) and len(token) > 20, f"TEST 6 FAILED verify-otp: no long JWT token returned: {verify_data}"
    user_from_verify = verify_data.get("user")
    assert user_from_verify and user_from_verify.get("uid") == t6_uid, f"TEST 6 FAILED: verify-otp user doesn't match login user"
    print(f"  [PASS] TEST 6: OTP verify SUCCESS. Authenticated JWT returned (length={len(token)}). Frontend would now redirect to HOME page.")

    # ---------- TEST 7 ----------
    print("\n" + "#" * 80)
    print("TEST 7: Profile page displays onboarding data belonging to correct user")
    print("#" * 80)
    # Get profile via /api/profile endpoint using token
    me_headers = {"Authorization": f"Bearer {token}"}
    profile_resp = make_request("GET", "/api/profile", headers=me_headers)
    assert profile_resp.status_code == 200, f"TEST 7 FAILED: GET /api/profile returned {profile_resp.status_code}. Body: {profile_resp.text}"
    profile_data = profile_resp.json()
    # Validate fields match TEST 1 signup
    check_fields = {
        "category": "OBC",
        "domicile": "Karnataka",
        "exam": "JEE Main",
        "examScore": "92",
        "careerOption": "Engineering",
        "preferredBranch": "Information Technology",
        "preferredLocation": "Bengaluru",
        "collegeType": "Private",
        "hostelRequired": False,
        "pwdCrossCategory": True,
    }
    all_match = True
    for k, expected in check_fields.items():
        actual = profile_data.get(k)
        match = actual == expected
        if not match:
            all_match = False
        print(f"    -> {k:20s} expected={expected!r:30s} actual={actual!r:30s} {'MATCH' if match else 'MISMATCH'}")
    assert all_match, "TEST 7 FAILED: Profile fields don't match TEST 1 signup onboarding payload"
    assert profile_data.get("uid") == t6_uid, f"TEST 7 FAILED: Profile uid {profile_data.get('uid')} != user uid {t6_uid}"
    assert profile_data.get("email") == NEW_EMAIL, f"TEST 7 FAILED: Profile email {profile_data.get('email')} != {NEW_EMAIL}"
    print("  [PASS] TEST 7: Profile data matches onboarding data for TEST 1 uid. Correct user's data displayed.")

    # Cleanup NEW_EMAIL user + profile (NOT the legacy account)
    print("\n" + "#" * 80)
    print("CLEANUP: Remove only TEST 1's brand-new user+profile (NOT legacy rajputshrinath349)")
    print("#" * 80)
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    try:
        du = await db["users"].delete_one({"uid": t6_uid})
        dp = await db["profiles"].delete_one({"uid": t6_uid})
        print(f"  Cleaned users={du.deleted_count}, profiles={dp.deleted_count} for test uid={t6_uid}")
    finally:
        await client.close()

    print("\n" + "=" * 80)
    print("ALL 7 TESTS PASSED!")
    print("=" * 80)
    print(f"""
    SUMMARY:
    - TEST 1 (New register): PASS (HTTP 200 + DB passwordHash present + verify_password OK)
    - TEST 2 (Correct pw login): PASS (200 + requiresOtp + otpPhone)
    - TEST 3 (Wrong pw login): PASS (401)
    - TEST 4 (Legacy email register with pw): PASS (UPDATE existing user + NO 409 + same _id + passwordHash now set)
    - TEST 5 (Legacy email correct pw login): PASS (200 + OTP stage + NO 'Phone OTP or Google' message)
    - TEST 6 (OTP verify): PASS (JWT returned, session authenticated)
    - TEST 7 (Profile page data): PASS (All onboarding fields match correct uid)
    """)


if __name__ == "__main__":
    asyncio.run(run_tests())
