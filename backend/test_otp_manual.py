#!/usr/bin/env python
"""
Manual OTP test script to verify Fast2SMS integration
"""
import json
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup path
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import after env is loaded
from routes import build_fast2sms_bulk_request

# Test data
PHONE = "918765432109"  # Indian number without + prefix
OTP = "123456"
MESSAGE = f"Your verification OTP is {OTP}. It is valid for 5 minutes."

print("\n" + "="*80)
print("MANUAL OTP TEST")
print("="*80)

# Get SMS config from environment
SMS_ROUTE = (os.getenv("SMS_ROUTE", "q") or "q").strip().lower()
SMS_SENDER_ID = (os.getenv("SMS_SENDER_ID", "FSTSMS") or "FSTSMS").strip()
SMS_TEMPLATE_ID = (os.getenv("SMS_TEMPLATE_ID") or "").strip()
SMS_ENTITY_ID = (os.getenv("SMS_ENTITY_ID") or os.getenv("SMS_PE_ID") or "").strip()

print(f"\n📋 SMS Configuration:")
print(f"  SMS_ROUTE: {SMS_ROUTE}")
print(f"  SMS_SENDER_ID: {SMS_SENDER_ID}")
print(f"  SMS_TEMPLATE_ID: {'<not set>' if not SMS_TEMPLATE_ID else SMS_TEMPLATE_ID}")
print(f"  SMS_ENTITY_ID: {'<not set>' if not SMS_ENTITY_ID else SMS_ENTITY_ID}")

# Build request
print(f"\n📞 Test OTP Request:")
print(f"  Phone: {PHONE}")
print(f"  OTP: {OTP}")
print(f"  Message: {MESSAGE}")

# Build payload
request_params = build_fast2sms_bulk_request(PHONE, MESSAGE, otp=OTP)

print(f"\n🔄 Request Payload for Fast2SMS bulkV2 API:")
print(json.dumps(request_params, indent=2))

# Check if API key is available
FAST_TO_SMS_API_KEY = os.getenv("FAST_TO_SMS_API_KEY")
if FAST_TO_SMS_API_KEY:
    print(f"\n✅ Fast2SMS API Key: Loaded ({len(FAST_TO_SMS_API_KEY)} chars)")
else:
    print(f"\n❌ Fast2SMS API Key: NOT LOADED")

print("\n" + "="*80)
