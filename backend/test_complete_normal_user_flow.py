import asyncio
import json
import sys
from pathlib import Path
import requests

BASE = "http://localhost:5000"

USER_EMAIL = "rajputshrinath349@gmail.com"
USER_PASS = "Shrinath@12345"
USER_PHONE = "9699510445"
WRONG_PASS = "WrongPassword@999"
WRONG_PHONE = "9999999999"
WRONG_OTP = "000000"

ADMIN_EMAIL = "ankitakenjale75@gmail.com"
ADMIN_PASS = "Ankita@123"

SUPER_ADMIN_EMAIL = "fourise@gmail.com"
SUPER_ADMIN_PASS = "123456"

def run_tests():
    print("=" * 80)
    print("COMPREHENSIVE TEST SUITE - NORMAL USER OTP LOGIN FLOW")
    print("=" * 80)

    # 1. Health check
    print("\n[TEST 1] Backend Health Check")
    r = requests.get(f"{BASE}/api/health", timeout=5)
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("  -> PASS: Backend is healthy and DB is connected.")

    # 2. Correct Gmail + Wrong Password
    print("\n[TEST 2] Correct Gmail + Wrong Password")
    r = requests.post(f"{BASE}/api/auth/login", json={"username": USER_EMAIL, "password": WRONG_PASS}, timeout=10)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    assert "Invalid username/email or password" in r.text, "Expected invalid credentials error"
    print("  -> PASS: Correct Gmail + wrong password rejected before any OTP.")

    # 3. Correct Gmail + Correct Password (Step 1 & 2: Must NOT return token, must return pending OTP challenge)
    print("\n[TEST 3] Correct Gmail + Correct Password -> Pending OTP State")
    r = requests.post(f"{BASE}/api/auth/login", json={"username": USER_EMAIL, "password": USER_PASS}, timeout=10)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    body = r.json()
    assert body.get("requiresOtp") is True or body.get("status") == "pending_otp", "Expected requiresOtp=True"
    assert "token" not in body or body.get("token") is None, "CRITICAL ERROR: Token MUST NOT be issued before OTP verification!"
    uid = body.get("uid") or body.get("user", {}).get("uid")
    assert bool(uid), "Expected user uid in pending login response"
    print(f"  -> PASS: User password valid, NO token issued, requiresOtp=True (uid={uid}).")

    # 4. Correct Gmail + Correct Password + Wrong Mobile Number
    print("\n[TEST 4] Wrong Mobile Number for User Account")
    r = requests.post(f"{BASE}/api/auth/login/send-otp", json={"uid": uid, "phone": WRONG_PHONE}, timeout=10)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "Phone number does not match this account" in r.text or "not match" in r.text, "Expected phone mismatch error"
    print("  -> PASS: Wrong mobile number correctly rejected.")

    # 5. Correct Gmail + Correct Password + Correct Mobile Number -> Send OTP
    print("\n[TEST 5] Correct Mobile Number -> Send OTP")
    r = requests.post(f"{BASE}/api/auth/login/send-otp", json={"uid": uid, "phone": USER_PHONE}, timeout=15)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    otp_resp = r.json()
    session_id = otp_resp.get("sessionId")
    assert bool(session_id), "Expected sessionId from send-otp"
    assert "otp" not in otp_resp, "CRITICAL: OTP must not be exposed in frontend response"
    print(f"  -> PASS: Real OTP triggered, sessionId={session_id}")

    # 6. Correct Gmail + Correct Password + Wrong OTP
    print("\n[TEST 6] Wrong OTP verification")
    r = requests.post(f"{BASE}/api/auth/login/verify-otp", json={
        "uid": uid,
        "phone": USER_PHONE,
        "otp": WRONG_OTP,
        "sessionId": session_id
    }, timeout=10)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "Invalid or expired OTP" in r.text, "Expected invalid OTP error"
    print("  -> PASS: Wrong OTP correctly rejected, no token issued.")

    # 7. Correct Gmail + Correct Password + Expired/Fake Session OTP
    print("\n[TEST 7] Invalid Session ID / Expired OTP")
    r = requests.post(f"{BASE}/api/auth/login/verify-otp", json={
        "uid": uid,
        "phone": USER_PHONE,
        "otp": "123456",
        "sessionId": "fake_expired_session_1234"
    }, timeout=10)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  -> PASS: Expired/invalid session correctly rejected.")

    # 8. Correct OTP -> Retrieve OTP from backend DB storage to test successful verification
    print("\n[TEST 8] Correct OTP verification from DB")
    from motor.motor_asyncio import AsyncIOMotorClient
    async def get_latest_otp():
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client["cutoffgrid"]
        doc = await db.otps.find_one({"session_id": session_id})
        if not doc:
            doc = await db.otps.find_one({"phone": USER_PHONE}, sort=[("created_at", -1)])
        return doc.get("otp") if doc else None

    import asyncio
    correct_otp = asyncio.run(get_latest_otp())
    print(f"  Retrieved OTP from DB for testing verification: {'Found' if bool(correct_otp) else 'Not Found'}")
    assert bool(correct_otp), "Could not find stored OTP in database"

    r = requests.post(f"{BASE}/api/auth/login/verify-otp", json={
        "uid": uid,
        "phone": USER_PHONE,
        "otp": str(correct_otp),
        "sessionId": session_id
    }, timeout=10)
    print(f"  Status: {r.status_code}, Body: {r.text}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    verify_resp = r.json()
    assert bool(verify_resp.get("token")), "Expected token on successful OTP verification"
    assert verify_resp.get("user", {}).get("role") == "USER", "Expected role USER"
    print(f"  -> PASS: Correct OTP verified! Token issued: {verify_resp.get('token')[:25]}... Role: {verify_resp.get('user', {}).get('role')}")

    # 9. Regression: Admin login
    print("\n[TEST 9] Regression: Admin Login")
    r = requests.post(f"{BASE}/api/admin/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS}, timeout=10)
    print(f"  Status: {r.status_code}, Role: {r.json().get('user', {}).get('role')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json().get("user", {}).get("role") == "ADMIN", "Expected role ADMIN"
    assert bool(r.json().get("token")), "Expected token for admin"
    print("  -> PASS: Admin login unchanged and functioning.")

    # 10. Regression: Super Admin login
    print("\n[TEST 10] Regression: Super Admin Login")
    r = requests.post(f"{BASE}/api/auth/login", json={"username": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASS}, timeout=10)
    print(f"  Status: {r.status_code}, Role: {r.json().get('user', {}).get('role')}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json().get("user", {}).get("role") == "SUPER_ADMIN", "Expected role SUPER_ADMIN"
    assert bool(r.json().get("token")), "Expected token for super admin"
    print("  -> PASS: Super Admin login unchanged and functioning.")

    print("\n" + "=" * 80)
    print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
