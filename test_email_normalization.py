#!/usr/bin/env python3
"""
Test email lookup and normalization in the login endpoint.
"""
import json
import urllib.request as urllib_request
import urllib.error as urllib_error
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"
LOGIN_ENDPOINT = urljoin(BASE_URL, "/api/auth/login")

# Test working user with different email formats
test_cases = [
    ("lowercase", {"email": "testuser9134@cutoffgrid.dev", "password": "Secure@TestPass123!"}),
    ("UPPERCASE", {"email": "TESTUSER9134@CUTOFFGRID.DEV", "password": "Secure@TestPass123!"}),
    ("mixed case", {"email": "TestUser9134@CutoffGrid.dev", "password": "Secure@TestPass123!"}),
    ("with spaces", {"email": "  testuser9134@cutoffgrid.dev  ", "password": "Secure@TestPass123!"}),
    ("with leading space", {"email": " testuser9134@cutoffgrid.dev", "password": "Secure@TestPass123!"}),
    ("with trailing space", {"email": "testuser9134@cutoffgrid.dev ", "password": "Secure@TestPass123!"}),
]

print(f"Testing email normalization on working user (testuser9134@cutoffgrid.dev)\n")
print("=" * 80)

for label, payload in test_cases:
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
    
    email_display = repr(payload["email"])
    if status == 200:
        print(f"✓ {label:20s} {email_display:50s} -> PASS (requiresOtp={requires_otp})")
    else:
        print(f"✗ {label:20s} {email_display:50s} -> FAIL ({status})")

print("=" * 80)
