#!/usr/bin/env python3
"""
Automated E2E authentication test with dev OTP.
Creates a new user, logs in, and verifies the complete flow.
"""
import json
import secrets
import urllib.request as urllib_request
import urllib.error as urllib_error
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

# Generate unique test credentials
test_id = secrets.token_hex(4).upper()
test_email = f"e2e-auto-{test_id}@cutoffgrid.dev"
test_phone = f"937{secrets.randbits(24):07d}"[:10]
test_password = "E2ETest@Secure123!"
test_name = f"E2E Test {test_id}"

print("=" * 80)
print("AUTOMATED E2E AUTHENTICATION TEST")
print("=" * 80)
print(f"Email: {test_email}")
print(f"Phone: {test_phone}")
print(f"Password: {test_password}")
print()

def make_request(endpoint, data=None):
    """Helper to make HTTP requests"""
    url = urljoin(BASE_URL, endpoint)
    try:
        request = urllib_request.Request(
            url,
            data=json.dumps(data).encode() if data else None,
            headers={"Content-Type": "application/json"},
        )
        with urllib_request.urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except urllib_error.HTTPError as error:
        try:
            return error.code, json.load(error)
        except:
            return error.code, {}
    except Exception as e:
        return 500, {"error": str(e)}

# STEP 1: Send OTP for signup
print("[1/5] Sending OTP...")
status, resp = make_request("/api/auth/send-otp", {
    "name": test_name,
    "email": test_email,
    "phone": test_phone,
})
if status != 200:
    print(f"✗ FAILED: {resp}")
    exit(1)
otp = resp.get("dev_otp")
session_id = resp.get("sessionId")
print(f"✓ OTP: {otp}, Session: {session_id[:8]}...")

# STEP 2: Verify OTP and create account
print("[2/5] Creating account...")
status, resp = make_request("/api/auth/verify-otp", {
    "name": test_name,
    "email": test_email,
    "phone": test_phone,
    "otp": otp,
    "sessionId": session_id,
    "registerPayload": {
        "name": test_name,
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "userType": "student",
    }
})
if status != 200:
    print(f"✗ FAILED: {resp}")
    exit(1)
uid = resp.get("user", {}).get("uid")
print(f"✓ Account created. UID: {uid}")

# STEP 3: Test login with email + password
print("[3/5] Testing login...")
status, resp = make_request("/api/auth/login", {
    "email": test_email,
    "password": test_password,
})
if status != 200:
    print(f"✗ FAILED: {resp}")
    exit(1)
if not resp.get("requiresOtp"):
    print(f"✗ FAILED: Expected requiresOtp=True")
    exit(1)
login_uid = resp.get("uid")
otp_phone = resp.get("otpPhone")
print(f"✓ Login verified. Phone for OTP: {otp_phone}")

# STEP 4: Send login OTP
print("[4/5] Sending login OTP...")
status, resp = make_request("/api/auth/login/send-otp", {
    "uid": login_uid,
    "phone": otp_phone,
})
if status != 200:
    print(f"✗ FAILED: {resp}")
    exit(1)
login_otp = resp.get("dev_otp")
login_session = resp.get("sessionId")
print(f"✓ Login OTP: {login_otp}, Session: {login_session[:8]}...")

# STEP 5: Verify login OTP
print("[5/5] Verifying OTP and logging in...")
status, resp = make_request("/api/auth/login/verify-otp", {
    "uid": login_uid,
    "phone": otp_phone,
    "otp": login_otp,
    "sessionId": login_session,
})
if status != 200:
    print(f"✗ FAILED: {resp}")
    exit(1)
token = resp.get("token")
final_user = resp.get("user", {})
print(f"✓ Successfully authenticated!")
print(f"  User: {final_user.get('email')}")
print(f"  Token: {token[:30]}...")

# BONUS: Test wrong password rejection
print("\n[BONUS] Testing wrong password rejection...")
status, resp = make_request("/api/auth/login", {
    "email": test_email,
    "password": "WrongPassword@123",
})
if status == 401:
    print(f"✓ Wrong password correctly rejected")
else:
    print(f"✗ FAILED: Expected 401, got {status}")
    exit(1)

print("\n" + "=" * 80)
print("✓✓✓ ALL TESTS PASSED ✓✓✓")
print("=" * 80)
print("\nCONCLUSION: Authentication system works correctly for new users!")
print("The newly created user can:")
print("  ✓ Sign up with email + password + OTP")
print("  ✓ Login with email + password + OTP")
print("  ✓ Reject wrong passwords")
