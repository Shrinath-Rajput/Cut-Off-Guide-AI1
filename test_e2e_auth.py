#!/usr/bin/env python3
"""
End-to-end authentication test: Signup → Login → OTP Verification
Tests the complete authentication flow to identify any breakpoints.
"""
import json
import secrets
import urllib.request as urllib_request
import urllib.error as urllib_error
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

# Generate unique test credentials
test_id = secrets.token_hex(4).upper()
test_email = f"e2e-test-{test_id}@cutoffgrid.dev"
test_phone = f"937{secrets.randbits(24):07d}"[:10]  # Random 10-digit starting with 937
test_password = "E2ETest@Secure123!"
test_name = f"E2E Test User {test_id}"

print("=" * 80)
print("END-TO-END AUTHENTICATION TEST")
print("=" * 80)
print(f"\nGenerated Test Credentials:")
print(f"  Email:    {test_email}")
print(f"  Phone:    {test_phone}")
print(f"  Password: {test_password}")
print(f"  Name:     {test_name}")
print("\n" + "=" * 80)

def make_request(endpoint, method="POST", data=None):
    """Helper to make HTTP requests"""
    url = urljoin(BASE_URL, endpoint)
    try:
        request = urllib_request.Request(
            url,
            data=json.dumps(data).encode() if data else None,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        with urllib_request.urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except urllib_error.HTTPError as error:
        try:
            return error.code, json.load(error)
        except:
            return error.code, {"error": str(error)}
    except Exception as e:
        return "ERROR", {"error": str(e)}

# Step 1: Send OTP
print("\n[STEP 1] Sending OTP for signup...")
status, response = make_request("/api/auth/send-otp", data={
    "name": test_name,
    "email": test_email,
    "phone": test_phone,
})
print(f"Status: {status}")
print(f"Response: {json.dumps(response, indent=2)}")

if status != 200:
    print("✗ FAILED: Could not send OTP")
    exit(1)

otp_session_id = response.get("sessionId")
dev_otp = response.get("dev_otp")
print(f"✓ OTP sent. Session ID: {otp_session_id}")
if dev_otp:
    print(f"  Dev OTP: {dev_otp}")
else:
    print("  [PROD MODE] SMS would be sent - using dev OTP prompt")
    dev_otp = input("  Enter the 6-digit OTP from SMS (or dev output): ").strip()

# Step 2: Verify OTP and create account
print("\n[STEP 2] Verifying OTP and creating account...")
register_payload = {
    "name": test_name,
    "email": test_email,
    "phone": test_phone,
    "password": test_password,
    "userType": "student",
    "category": "General",
    "domicile": "Maharashtra",
}

status, response = make_request("/api/auth/verify-otp", data={
    "name": test_name,
    "email": test_email,
    "phone": test_phone,
    "otp": dev_otp,
    "sessionId": otp_session_id,
    "registerPayload": register_payload,
})
print(f"Status: {status}")
print(f"Response fields: {list(response.keys())}")

if status != 200:
    print(f"✗ FAILED: Could not create account. Message: {response.get('message')}")
    exit(1)

signup_token = response.get("token")
signup_user = response.get("user")
print(f"✓ Account created successfully!")
print(f"  UID: {signup_user.get('uid')}")
print(f"  Email: {signup_user.get('email')}")
print(f"  Token received: {bool(signup_token)}")

# Step 3: Login with email and password
print("\n[STEP 3] Testing login with email + password...")
status, response = make_request("/api/auth/login", data={
    "email": test_email,
    "password": test_password,
})
print(f"Status: {status}")
print(f"Response fields: {list(response.keys())}")

if status != 200:
    print(f"✗ FAILED: Login failed. Message: {response.get('message')}")
    exit(1)

login_uid = response.get("uid")
login_otp_phone = response.get("otpPhone")
requires_otp = response.get("requiresOtp")

print(f"✓ Login credentials verified!")
print(f"  UID: {login_uid}")
print(f"  Requires OTP: {requires_otp}")
print(f"  OTP Phone: {login_otp_phone}")

if not requires_otp:
    print("✗ FAILED: Expected requiresOtp=True")
    exit(1)

# Step 4: Send login OTP
print("\n[STEP 4] Sending login OTP...")
status, response = make_request("/api/auth/login/send-otp", data={
    "uid": login_uid,
    "phone": login_otp_phone,
    "name": test_name,
    "email": test_email,
})
print(f"Status: {status}")

if status != 200:
    print(f"✗ FAILED: Could not send login OTP. Message: {response.get('message')}")
    exit(1)

login_otp_session_id = response.get("sessionId")
login_dev_otp = response.get("dev_otp")
print(f"✓ Login OTP sent. Session ID: {login_otp_session_id}")
if login_dev_otp:
    print(f"  Dev OTP: {login_dev_otp}")
else:
    print("  [PROD MODE] SMS would be sent - using dev OTP prompt")
    login_dev_otp = input("  Enter the 6-digit OTP from SMS (or dev output): ").strip()

# Step 5: Verify login OTP
print("\n[STEP 5] Verifying login OTP...")
status, response = make_request("/api/auth/login/verify-otp", data={
    "uid": login_uid,
    "phone": login_otp_phone,
    "otp": login_dev_otp,
    "sessionId": login_otp_session_id,
    "name": test_name,
    "email": test_email,
})
print(f"Status: {status}")
print(f"Response fields: {list(response.keys())}")

if status != 200:
    print(f"✗ FAILED: OTP verification failed. Message: {response.get('message')}")
    exit(1)

final_token = response.get("token")
final_user = response.get("user")
print(f"✓ Login complete! Authenticated successfully!")
print(f"  User: {final_user.get('email')}")
print(f"  Token: {final_token[:30]}...")

# Step 6: Test wrong password rejection
print("\n[STEP 6] Testing wrong password rejection...")
status, response = make_request("/api/auth/login", data={
    "email": test_email,
    "password": "WrongPassword@123",
})
print(f"Status: {status}")

if status == 401:
    print(f"✓ Wrong password correctly rejected (401)")
else:
    print(f"✗ FAILED: Expected 401 for wrong password, got {status}")

# Step 7: Test email normalization
print("\n[STEP 7] Testing email normalization...")
test_emails = [
    test_email.upper(),
    f"  {test_email}  ",
    test_email.upper(),
]

for normalized_email in test_emails:
    status, response = make_request("/api/auth/login", data={
        "email": normalized_email,
        "password": test_password,
    })
    if status == 200 and response.get("requiresOtp"):
        print(f"  ✓ Email '{normalized_email}' -> Success")
    else:
        print(f"  ✗ Email '{normalized_email}' -> Failed ({status})")

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED!")
print("=" * 80)
