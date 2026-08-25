#!/usr/bin/env python3
"""
Test login endpoint with multiple users to identify authentication issues.
"""
import json
import urllib.request as urllib_request
import urllib.error as urllib_error
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"
LOGIN_ENDPOINT = urljoin(BASE_URL, "/api/auth/login")

# Test cases with different users
test_users = [
    {
        "label": "rajputshrinath129@gmail.com (supposedly works)",
        "email": "rajputshrinath129@gmail.com",
        "password": "Secure@TestPass123!",
    },
    {
        "label": "testuser9134@cutoffgrid.dev",
        "email": "testuser9134@cutoffgrid.dev",
        "password": "Secure@TestPass123!",
    },
    {
        "label": "testuser7034@cutoffgrid.dev",
        "email": "testuser7034@cutoffgrid.dev",
        "password": "Secure@TestPass123!",
    },
    {
        "label": "rajputshrinath349@gmail.com",
        "email": "rajputshrinath349@gmail.com",
        "password": "Secure@TestPass123!",
    },
    {
        "label": "wrong password for user",
        "email": "rajputshrinath129@gmail.com",
        "password": "wrong-password-12345",
    },
]

print(f"Testing login endpoint at: {LOGIN_ENDPOINT}\n")
print("=" * 70)

for test in test_users:
    label = test["label"]
    payload = {
        "email": test["email"],
        "password": test["password"],
    }
    
    try:
        request = urllib_request.Request(
            LOGIN_ENDPOINT,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib_request.urlopen(request, timeout=10) as response:
            status = response.status
            body = json.load(response)
    except urllib_error.HTTPError as error:
        status = error.code
        try:
            body = json.load(error)
        except:
            body = {"status": "error", "message": str(error)}
    except Exception as e:
        status = "ERROR"
        body = {"status": "error", "message": str(e)}
    
    result_status = body.get("status", "unknown")
    result_message = body.get("message", "no message")
    requires_otp = body.get("requiresOtp", False)
    
    print(f"Test: {label}")
    print(f"  Email:        {test['email']}")
    print(f"  HTTP Status:  {status}")
    print(f"  Status:       {result_status}")
    print(f"  Message:      {result_message}")
    print(f"  Requires OTP: {requires_otp}")
    print()

print("=" * 70)
