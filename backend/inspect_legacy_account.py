"""Diagnostic: Inspect ALL records for rajputshrinath349@gmail.com
   Mask ALL sensitive fields. Never print passwordHash or actual credentials.
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / ".venv" / "Lib" / "site-packages"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.auth_service import normalize_phone

TARGET_EMAIL = "rajputshrinath349@gmail.com"
TARGET_EMAIL_NORM = TARGET_EMAIL.strip().lower()
TARGET_PHONE_RAW = "9699510445"


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
    print(f"[INFO] Connecting to MongoDB database={db_name}")

    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command("ping")
        print("[OK] DB connected")
    except Exception as e:
        print(f"[FAIL] DB connect error: {e}")
        return

    db = client[db_name]
    users = db["users"]
    profiles = db["profiles"]

    print("\n" + "=" * 80)
    print(f"SEARCHING USERS FOR EMAIL (case-insensitive, strip): {TARGET_EMAIL}")
    print("=" * 80)

    # Also get ALL users to scan for normalized email to catch non-normalized storage
    all_users = await users.find({}).to_list(length=10000)

    matching_users = []
    for u in all_users:
        stored_email = u.get("email")
        if stored_email and isinstance(stored_email, str):
            if stored_email.strip().lower() == TARGET_EMAIL_NORM:
                matching_users.append(u)

    # Also scan by phone (both normalizations)
    print(f"\n[INFO] Also scanning for phone match: {TARGET_PHONE_RAW}")
    try:
        target_phone_norm = normalize_phone(TARGET_PHONE_RAW)
    except Exception:
        target_phone_norm = None

    phone_matches = []
    for u in all_users:
        sp = u.get("phone")
        matched = False
        if sp:
            if sp == TARGET_PHONE_RAW:
                matched = True
            else:
                try:
                    if normalize_phone(sp) == target_phone_norm:
                        matched = True
                except Exception:
                    pass
        if matched:
            phone_matches.append(u)

    print(f"\n[RESULT] Email-matching user count: {len(matching_users)}")
    print(f"[RESULT] Phone-matching user count: {len(phone_matches)}")

    # Deduplicate combined
    seen_ids = set()
    combined = []
    for u in matching_users + phone_matches:
        uid = str(u.get("_id"))
        if uid not in seen_ids:
            seen_ids.add(uid)
            combined.append(u)
    print(f"[RESULT] Combined unique (email OR phone match): {len(combined)}")

    for idx, u in enumerate(combined, 1):
        print("\n" + "-" * 80)
        print(f"RECORD #{idx}")
        print("-" * 80)
        print(f"  _id              : {u.get('_id')}")
        print(f"  uid              : {u.get('uid')}")
        print(f"  name             : {u.get('name')}")
        print(f"  email (raw)      : {repr(u.get('email'))}")
        print(f"  email (norm cmp) : {'MATCH' if (u.get('email') and u.get('email').strip().lower() == TARGET_EMAIL_NORM) else 'NO_MATCH'}")
        print(f"  phone (raw)      : {repr(u.get('phone'))}")
        ph = u.get("phone")
        if ph:
            try:
                ph_norm = normalize_phone(ph)
                print(f"  phone (norm)     : {ph_norm}")
                print(f"  phone matches tgt: {'YES' if ph_norm == target_phone_norm else 'NO'}")
            except Exception as e:
                print(f"  phone (norm)     : ERROR {e}")
        print(f"  provider         : {u.get('provider')}")
        print(f"  role             : {u.get('role')}")
        has_ph = bool(u.get("passwordHash") or u.get("password_hash") or u.get("password"))
        print(f"  has passwordHash : {'YES' if has_ph else 'NO'}  (actual value NEVER printed)")
        if u.get("passwordHash") is None and u.get("password_hash") is None:
            print(f"  passwordHash field PRESENT in doc? : {('passwordHash' in u) or ('password_hash' in u)}")
        print(f"  createdAt        : {u.get('createdAt')}")
        print(f"  lastLogin        : {u.get('lastLogin')}")
        # Print other top-level keys (NOT their values, just names — avoid leaking)
        other_keys = [k for k in u.keys() if k not in {"_id","uid","name","email","phone","provider","role","passwordHash","password_hash","password","createdAt","lastLogin"}]
        print(f"  other fields     : {other_keys}")

        # Check if profile exists for this uid
        uid_val = u.get("uid")
        if uid_val:
            prof = await profiles.find_one({"uid": uid_val})
            if prof:
                print(f"  PROFILE linked   : YES (profile._id={prof.get('_id')})")
                # Print profile keys
                pfields = [k for k in prof.keys() if k not in {"_id","uid","createdAt","updatedAt"}]
                print(f"    profile fields : {pfields}")
                for pf in ["category","domicile","exam","examScore","careerOption","preferredBranch","preferredLocation","budgetRange","collegeType","hostelRequired"]:
                    if pf in prof:
                        print(f"    -> {pf:20s}: {prof[pf]}")
            else:
                print(f"  PROFILE linked   : NONE (uid={uid_val} not in profiles)")

    # Check indexes
    print("\n" + "=" * 80)
    print("USERS COLLECTION INDEXES (for duplicate detection):")
    print("=" * 80)
    try:
        idxs = await users.index_information()
        for name, spec in idxs.items():
            print(f"  {name} -> keys={spec.get('key')}, unique={spec.get('unique')}")
    except Exception as e:
        print(f"  ERROR reading indexes: {e}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
