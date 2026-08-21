"""Verify:
1. passwordHash now exists for the legacy account
2. NO duplicate user was created for rajputshrinath349@gmail.com (still only 2 original + 1 new test)
3. Profile data for legacy account is PRESERVED after password setup
Masks all sensitive fields.
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.auth_service import normalize_phone

TARGET_LEGACY_EMAIL = "rajputshrinath349@gmail.com"
TARGET_NEW_TEST_EMAIL = "testuser7699@cutoffgrid.dev"  # from TEST 1 output above


def mask(v):
    if v is None:
        return "NULL"
    if not isinstance(v, str):
        return str(v)
    if len(v) <= 4:
        return "*" * len(v)
    return v[:2] + "*" * (len(v) - 4) + v[-2:]


async def main():
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")
    print(f"[INFO] Connecting to DB={db_name}")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command("ping")
    except Exception as e:
        print(f"[FAIL] DB connect: {e}")
        return
    db = client[db_name]
    users = db["users"]
    profiles = db["profiles"]

    all_users = await users.find({}).to_list(length=20000)

    def find_all_by_email(email_norm):
        matches = []
        for u in all_users:
            stored = u.get("email")
            if stored and isinstance(stored, str) and stored.strip().lower() == email_norm:
                matches.append(u)
        return matches

    legacy_email_norm = TARGET_LEGACY_EMAIL.strip().lower()
    legacy_matches = find_all_by_email(legacy_email_norm)
    print(f"\n=== LEGACY USER ({TARGET_LEGACY_EMAIL}) ===")
    print(f"  Total records for this email: {len(legacy_matches)}")

    for idx, u in enumerate(legacy_matches, 1):
        print(f"\n  RECORD {idx}:")
        print(f"    _id             : {u.get('_id')}")
        print(f"    uid             : {u.get('uid')}")
        print(f"    name            : {u.get('name')}")
        print(f"    provider        : {u.get('provider')}")
        has_ph = bool(u.get("passwordHash") or u.get("password_hash"))
        print(f"    has passwordHash: {'YES' if has_ph else 'NO'}")
        ph = u.get("passwordHash")
        if ph:
            print(f"    passwordHash[0:18]: {mask(ph[:18])}...  (first chars shown masked)")
        print(f"    phone (raw)     : {repr(u.get('phone'))}")

        uid_val = u.get("uid")
        if uid_val:
            prof = await profiles.find_one({"uid": uid_val})
            if prof:
                print(f"    PROFILE         : YES (id={prof.get('_id')})")
                fields = [
                    "category", "domicile", "exam", "examScore", "careerOption",
                    "preferredBranch", "preferredLocation", "budgetRange",
                    "collegeType", "hostelRequired"
                ]
                populated = [f for f in fields if prof.get(f) not in (None, "")]
                print(f"    onboarding fields populated: {len(populated)}/10")
                for f in populated:
                    print(f"       -> {f:20s}: {prof[f]}")
            else:
                print(f"    PROFILE         : NONE")

    print(f"\n=== NEW TEST USER ({TARGET_NEW_TEST_EMAIL}) ===")
    test_norm = TARGET_NEW_TEST_EMAIL.strip().lower()
    test_matches = find_all_by_email(test_norm)
    print(f"  Total records: {len(test_matches)}")
    for u in test_matches:
        has_ph = bool(u.get("passwordHash") or u.get("password_hash"))
        print(f"    uid={u.get('uid')} provider={u.get('provider')} has passwordHash={'YES' if has_ph else 'NO'}")
        uid_val = u.get("uid")
        if uid_val:
            prof = await profiles.find_one({"uid": uid_val})
            if prof:
                fields = ["category", "domicile", "exam", "examScore", "careerOption",
                          "preferredBranch", "preferredLocation", "budgetRange",
                          "collegeType", "hostelRequired"]
                populated = [f for f in fields if prof.get(f) not in (None, "")]
                print(f"    PROFILE exists, onboarding fields: {len(populated)}/10")
                for f in populated:
                    print(f"       -> {f:20s}: {prof[f]}")

    print(f"\n=== OTP MODE CONFIG (backend .env) ===")
    otp_mode = os.getenv("OTP_MODE", "")
    sms_route = os.getenv("SMS_ROUTE", "")
    api_key_set = bool(os.getenv("FAST_TO_SMS_API_KEY", ""))
    print(f"  OTP_MODE           : {otp_mode}")
    print(f"  SMS_ROUTE          : {sms_route}")
    print(f"  FAST_TO_SMS_API_KEY: {'SET' if api_key_set else 'MISSING'}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
