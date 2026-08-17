#!/usr/bin/env python
"""
Test Fast2SMS request directly
"""
import json
import logging
import os
import sys
from pathlib import Path
from urllib import request as urllib_request
from urllib import error as urllib_error

from dotenv import load_dotenv

# Setup
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get config
FAST_TO_SMS_API_KEY = os.getenv("FAST_TO_SMS_API_KEY")
SMS_ROUTE = (os.getenv("SMS_ROUTE", "q") or "q").strip().lower()
SMS_LANGUAGE = (os.getenv("SMS_LANGUAGE", "english") or "english").strip().lower()
SMS_FLASH = (os.getenv("SMS_FLASH", "0") or "0").strip()

print("\n" + "="*80)
print("FAST2SMS API REQUEST TEST")
print("="*80)

# Test parameters
PHONE = "918765432109"
OTP = "123456"
MESSAGE = f"Your verification OTP is {OTP}. It is valid for 5 minutes."

# Build payload (matching the fixed route "q" format)
request_params = {
    "numbers": PHONE,
    "message": MESSAGE,
    "route": SMS_ROUTE,
    "language": SMS_LANGUAGE,
    "flash": SMS_FLASH,
}

print(f"\n📋 Configuration:")
print(f"  SMS_ROUTE: {SMS_ROUTE}")
print(f"  FAST_TO_SMS_API_KEY loaded: {'YES' if FAST_TO_SMS_API_KEY else 'NO'}")

print(f"\n📤 Request Payload:")
print(json.dumps(request_params, indent=2))

if not FAST_TO_SMS_API_KEY:
    print("\n❌ FAST_TO_SMS_API_KEY is not configured!")
    sys.exit(1)

# Make the request to Fast2SMS
print(f"\n🔄 Making request to Fast2SMS bulkV2 API...")

url = "https://www.fast2sms.com/dev/bulkV2"
data = json.dumps(request_params).encode("utf-8")
headers = {
    "authorization": FAST_TO_SMS_API_KEY,
    "Content-Type": "application/json",
}

req = urllib_request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib_request.urlopen(req, timeout=20) as response:
        response_text = response.read().decode("utf-8", "ignore")
        status_code = response.status
        
        try:
            response_json = json.loads(response_text)
        except:
            response_json = response_text
        
        print(f"\n✅ SUCCESS - HTTP {status_code}")
        print(f"\n📥 Response from Fast2SMS:")
        if isinstance(response_json, dict):
            print(json.dumps(response_json, indent=2))
        else:
            print(response_json)
        
        # Check for success indicators
        is_success = False
        if isinstance(response_json, dict):
            if response_json.get("return") in (True, "true", "True", "1", 1):
                is_success = True
            elif str(response_json.get("status", "")).lower() == "success":
                is_success = True
            elif response_json.get("request_id"):
                is_success = True
        
        print(f"\n🎯 Fast2SMS indicated success: {'✅ YES' if is_success else '⚠️  Unclear (check response above)'}")

except urllib_error.HTTPError as exc:
    error_body = exc.read().decode("utf-8", "ignore")
    try:
        error_json = json.loads(error_body)
    except:
        error_json = error_body
    
    print(f"\n❌ FAILED - HTTP {exc.code}")
    print(f"\n📥 Error Response from Fast2SMS:")
    if isinstance(error_json, dict):
        print(json.dumps(error_json, indent=2))
    else:
        print(error_json)

except Exception as e:
    print(f"\n❌ FAILED - {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
