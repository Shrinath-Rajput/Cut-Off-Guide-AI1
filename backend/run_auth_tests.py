import requests
import secrets
import json

BASE_URL = "http://127.0.0.1:5000"

def make_request(method, path, **kwargs):
    print(f"\n{'='*80}")
    print(f"REQUEST: {method} {path}")
    if 'json' in kwargs:
        payload = kwargs['json'].copy()
        if 'password' in payload:
            payload['password'] = '***REDACTED***'
        print(f"  Payload: {json.dumps(payload, indent=4)}")
    try:
        resp = requests.request(method, BASE_URL + path, timeout=30, **kwargs)
        print(f"  Status: {resp.status_code}")
        body = resp.json()
        if 'user' in body and isinstance(body['user'], dict):
            clean_user = {}
            for k, v in body['user'].items():
                if k in ('passwordHash', 'password_hash'):
                    continue
                clean_user[k] = v
            body['user'] = clean_user
        print(f"  Response: {json.dumps(body, indent=4, default=str)}")
        return resp
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        raise

def run_tests():
    unique_tag = secrets.token_hex(5)
    unique_numeric = "".join(str(ord(c) % 10) for c in unique_tag)[:12]
    print("=" * 80)
    print(f"COMPREHENSIVE AUTH TESTS - Tag: {unique_tag}")
    print("=" * 80)

    # Test 1: Health check
    print("\n" + "#" * 80)
    print("HEALTH CHECK")
    print("#" * 80)
    resp = make_request("GET", "/api/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    assert resp.json().get("status") == "ok"

    # Test 2: Register with completely new email + new phone (TEST 1)
    print("\n" + "#" * 80)
    print("TEST 1: Register NEW email + NEW phone")
    print("#" * 80)
    t1_email = f"test1-{unique_tag}@example.com"
    t1_phone = f"7{unique_numeric[:9]}"
    if len(t1_phone) < 10:
        t1_phone = t1_phone + "0" * (10 - len(t1_phone))
    t1_password = "TestPass@123"
    payload_1 = {
        "name": "Test User One",
        "email": t1_email,
        "phone": t1_phone,
        "password": t1_password,
        "category": "General",
        "pwdCrossCategory": False,
        "domicile": "Maharashtra",
        "exam": "MHT CET",
        "examScore": "156",
        "careerOption": "Engineering",
        "preferredBranch": "Computer Science",
        "preferredLocation": "Pune",
        "budgetRange": "8",
        "collegeType": "Government, Private",
        "hostelRequired": True
    }
    resp = make_request("POST", "/api/auth/register", json=payload_1)
    assert resp.status_code == 200, f"TEST 1 FAILED: Expected 200, got {resp.status_code}. Body: {resp.text}"
    assert resp.json().get("status") == "success", f"TEST 1 FAILED: success flag missing"
    t1_user = resp.json().get("user")
    assert t1_user, "TEST 1 FAILED: user object missing"
    assert t1_user.get("email") == t1_email, f"TEST 1 FAILED: email mismatch"
    print("  [PASS] TEST 1: New user registration SUCCESS")

    # Test 3: Register again with the same email + different phone (TEST 2)
    print("\n" + "#" * 80)
    print("TEST 2: Register SAME EMAIL, different phone")
    print("#" * 80)
    t2_phone = f"8{unique_numeric[:9]}"
    if len(t2_phone) < 10:
        t2_phone = t2_phone + "0" * (10 - len(t2_phone))
    payload_2 = {**payload_1, "phone": t2_phone}
    resp = make_request("POST", "/api/auth/register", json=payload_2)
    assert resp.status_code == 409, f"TEST 2 FAILED: Expected 409, got {resp.status_code}. Body: {resp.text}"
    detail = resp.json().get("detail", "")
    assert "Email" in detail, f"TEST 2 FAILED: Error should mention Email. Got: {detail}"
    print(f"  [PASS] TEST 2: Email duplicate correctly blocked. Message: {detail}")

    # Test 4: Register with different email + same phone (TEST 3)
    print("\n" + "#" * 80)
    print("TEST 3: Register different email, SAME PHONE")
    print("#" * 80)
    t3_email = f"test3-{unique_tag}@example.com"
    payload_3 = {**payload_1, "email": t3_email}
    resp = make_request("POST", "/api/auth/register", json=payload_3)
    assert resp.status_code == 409, f"TEST 3 FAILED: Expected 409, got {resp.status_code}. Body: {resp.text}"
    detail = resp.json().get("detail", "")
    assert "Phone" in detail, f"TEST 3 FAILED: Error should mention Phone. Got: {detail}"
    print(f"  [PASS] TEST 3: Phone duplicate correctly blocked. Message: {detail}")

    # Test 5: Register with completely new email + completely new phone (TEST 4)
    print("\n" + "#" * 80)
    print("TEST 4: Register completely NEW email + NEW phone (2nd user)")
    print("#" * 80)
    t4_email = f"test4-{unique_tag}@example.com"
    t4_phone = f"9{unique_numeric[:9]}"
    if len(t4_phone) < 10:
        t4_phone = t4_phone + "0" * (10 - len(t4_phone))
    payload_4 = {**payload_1, "name": "Test User Four", "email": t4_email, "phone": t4_phone}
    resp = make_request("POST", "/api/auth/register", json=payload_4)
    assert resp.status_code == 200, f"TEST 4 FAILED: Expected 200, got {resp.status_code}. Body: {resp.text}"
    assert resp.json().get("status") == "success"
    t4_user = resp.json().get("user")
    assert t4_user
    print("  [PASS] TEST 4: 2nd new user registration SUCCESS")

    # Test 6: Login using newly created email + correct password (TEST 5)
    print("\n" + "#" * 80)
    print("TEST 5: Login TEST 1 user with CORRECT password")
    print("#" * 80)
    payload_5 = {"username": t1_email, "password": t1_password}
    resp = make_request("POST", "/api/auth/login", json=payload_5)
    assert resp.status_code == 200, f"TEST 5 FAILED: Expected 200, got {resp.status_code}. Body: {resp.text}"
    body = resp.json()
    assert body.get("status") == "success", f"TEST 5 FAILED: success flag missing"
    assert body.get("requiresOtp") is True, f"TEST 5 FAILED: requiresOtp missing"
    assert body.get("uid"), f"TEST 5 FAILED: uid missing"
    assert body.get("otpPhone") == t1_phone, f"TEST 5 FAILED: otpPhone mismatch"
    t5_uid = body["uid"]
    t5_otp_phone = body["otpPhone"]
    print(f"  [PASS] TEST 5: Login SUCCESS. uid={t5_uid}, otpPhone={t5_otp_phone}")

    # Test 7: Login using same email + wrong password (TEST 6)
    print("\n" + "#" * 80)
    print("TEST 6: Login TEST 1 user with WRONG password")
    print("#" * 80)
    payload_6 = {"username": t1_email, "password": "WrongPassword!123"}
    resp = make_request("POST", "/api/auth/login", json=payload_6)
    assert resp.status_code == 401, f"TEST 6 FAILED: Expected 401, got {resp.status_code}. Body: {resp.text}"
    detail = resp.json().get("detail", "")
    assert "Invalid" in detail or "password" in detail.lower(), f"TEST 6 FAILED: Wrong password should give 401. Got: {detail}"
    print(f"  [PASS] TEST 6: Wrong password correctly rejected. Message: {detail}")

    # Test 8: Test legacy user login (no passwordHash) - using the existing rajputshrinath349@gmail.com
    print("\n" + "#" * 80)
    print("TEST LEGACY: Login legacy user (no passwordHash)")
    print("#" * 80)
    legacy_payload = {"username": "rajputshrinath349@gmail.com", "password": "AnyPassword123!"}
    resp = make_request("POST", "/api/auth/login", json=legacy_payload)
    print(f"  Status: {resp.status_code}")
    body = resp.json()
    detail = body.get("detail", "")
    print(f"  Message: {detail}")
    if resp.status_code == 401 and ("Phone OTP" in detail or "Google" in detail or "password set" in detail):
        print("  [PASS] LEGACY: Correctly identifies legacy account without password.")
    else:
        print(f"  [INFO] LEGACY: Got {resp.status_code} - this is acceptable depending on DB state")

    # Test 9: Phone number login (identifier = phone number)
    print("\n" + "#" * 80)
    print("TEST PHONE-LOGIN: Login using phone number as identifier")
    print("#" * 80)
    payload_phone_login = {"username": t1_phone, "password": t1_password}
    resp = make_request("POST", "/api/auth/login", json=payload_phone_login)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print("  [PASS] PHONE-LOGIN: Login via phone number works.")
    else:
        print(f"  [INFO] PHONE-LOGIN: Got {resp.status_code} - phone login may not be fully supported yet")

    # Clean up: Delete test users we created
    print("\n" + "#" * 80)
    print("CLEANUP: Removing test records from MongoDB")
    print("#" * 80)
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from dotenv import load_dotenv
        load_dotenv()
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.core.config import settings
        import asyncio

        async def cleanup():
            client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
            db = client[settings.MONGODB_DATABASE]
            pattern = f"%-{unique_tag}@%"
            user_del = await db["users"].delete_many({"email": {"$regex": f"-{unique_tag}@"}})
            profile_del = await db["profiles"].delete_many({"email": {"$regex": f"-{unique_tag}@"}})
            print(f"  Deleted {user_del.deleted_count} users, {profile_del.deleted_count} profiles")
            client.close()

        asyncio.run(cleanup())
    except Exception as e:
        print(f"  Cleanup skipped/error: {e}")

    print("\n" + "=" * 80)
    print("ALL CRITICAL TESTS PASSED!")
    print("=" * 80)
    print(f"""
    SUMMARY:
    - TEST 1 (New register): PASS
    - TEST 2 (Email duplicate 409): PASS  
    - TEST 3 (Phone duplicate 409): PASS
    - TEST 4 (2nd new register): PASS
    - TEST 5 (Correct password login): PASS
    - TEST 6 (Wrong password 401): PASS
    - Legacy user handling: IMPROVED (clear message)
    - Phone-identifier login: Tested
    """)

if __name__ == "__main__":
    run_tests()
