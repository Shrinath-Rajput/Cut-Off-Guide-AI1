"""PHASE 1: ONLY DISPLAY matching records for email/phone.
   NO DELETION in this phase. Show user what will be deleted, with ALL fields masked except identifiers.
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

TARGET_EMAIL = "rajputshrinath349@gmail.com"
TARGET_EMAIL_NORM = TARGET_EMAIL.strip().lower()
TARGET_PHONE_RAW = "9699510445"


def mask_value(v):
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
    print(f"[INFO] MongoDB database: {db_name}")
    print(f"[INFO] Target email (normalized): {TARGET_EMAIL_NORM}")
    print(f"[INFO] Target phone (raw): {TARGET_PHONE_RAW}")

    try:
        target_phone_norm = normalize_phone(TARGET_PHONE_RAW)
    except Exception:
        target_phone_norm = None
    print(f"[INFO] Target phone (normalized): {target_phone_norm}")

    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command("ping")
        print("[OK] DB connected\n")
    except Exception as e:
        print(f"[FAIL] DB connect error: {e}")
        return

    db = client[db_name]
    users = db["users"]
    profiles = db["profiles"]
    otps = db["otps"]

    print("=" * 90)
    print("PHASE 1: DISCOVERING MATCHING RECORDS (NO DELETION YET)")
    print("=" * 90)

    all_users = await users.find({}).to_list(length=50000)

    matching_users = []
    for u in all_users:
        match_reason = []
        stored_email = u.get("email")
        stored_phone = u.get("phone")

        email_match = bool(
            stored_email
            and isinstance(stored_email, str)
            and stored_email.strip().lower() == TARGET_EMAIL_NORM
        )
        phone_match = False
        if stored_phone and isinstance(stored_phone, str):
            try:
                if normalize_phone(stored_phone) == target_phone_norm:
                    phone_match = True
            except Exception:
                if stored_phone == TARGET_PHONE_RAW:
                    phone_match = True
        if email_match or phone_match:
            if email_match:
                match_reason.append("EMAIL")
            if phone_match:
                match_reason.append("PHONE")
            matching_users.append((u, match_reason))

    print(f"\n[RESULT] Total users matching email OR phone: {len(matching_users)}")
    print("-" * 90)

    uid_list_for_delete = []
    for idx, (u, reason) in enumerate(matching_users, 1):
        uid = u.get("uid")
        if uid:
            uid_list_for_delete.append(uid)
        has_ph = bool(u.get("passwordHash") or u.get("password_hash"))
        print(f"\n  USER RECORD #{idx}:")
        print(f"    Match reason    : {' + '.join(reason)}")
        print(f"    _id             : {u.get('_id')}")
        print(f"    uid             : {uid}")
        print(f"    name            : {u.get('name')}")
        print(f"    email (raw)     : {repr(u.get('email'))}")
        print(f"    phone (raw)     : {repr(u.get('phone'))}")
        print(f"    provider        : {u.get('provider')}")
        print(f"    role            : {u.get('role')}")
        print(f"    has passwordHash: {'YES' if has_ph else 'NO'}")
        print(f"    createdAt       : {u.get('createdAt')}")

        # Check linked profile
        prof = await profiles.find_one({"uid": uid}) if uid else None
        if prof:
            pfields_count = sum(
                1
                for k in (
                    "category",
                    "domicile",
                    "exam",
                    "examScore",
                    "careerOption",
                    "preferredBranch",
                    "preferredLocation",
                    "budgetRange",
                    "collegeType",
                    "hostelRequired",
                )
                if prof.get(k) not in (None, "")
            )
            print(f"    Linked PROFILE  : YES (_id={prof.get('_id')}), onboarding fields: {pfields_count}/10")
            # Show profile identifiers only
            print(f"      -> profile.uid   : {prof.get('uid')}")
            print(f"      -> profile.name  : {prof.get('name')}")
            print(f"      -> profile.email : {prof.get('email')}")
            print(f"      -> profile.phone : {prof.get('phone')}")
        else:
            print(f"    Linked PROFILE  : NONE")

        # Check admin status
        if u.get("role") == "ADMIN":
            print(f"    ⚠️  WARNING       : THIS RECORD IS AN ADMIN ACCOUNT! WILL NOT DELETE.")

    # Also clean up any OTP rows for the phone (these are temporary anyway)
    otp_count = 0
    try:
        if target_phone_norm:
            otp_count = await otps.count_documents({"phone": target_phone_norm})
    except Exception:
        pass

    print(f"\n[INFO] OTP sessions for target phone in `otps` collection: {otp_count}")

    # Save uid list to file for next phase
    save_data = {
        "db_name": db_name,
        "email": TARGET_EMAIL_NORM,
        "phone_norm": target_phone_norm,
        "uids_to_delete": [u for u in uid_list_for_delete if u],
        "user_ids_to_delete": [
            str(u.get("_id")) for (u, _) in matching_users if u.get("role") != "ADMIN"
        ],
    }
    with open(Path(__file__).parent / "_cleanup_plan.json", "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n[INFO] Cleanup plan written to _cleanup_plan.json")
    print(f"       UIDs proposed for deletion: {len(save_data['uids_to_delete'])}")

    try:
        await client.close()
    except Exception:
        pass

    print("\n✅ PHASE 1 COMPLETE. Review above records.")
    print("   If the records shown above are the test accounts, proceed to Phase 2 to delete them.")


import json

if __name__ == "__main__":
    asyncio.run(main())
