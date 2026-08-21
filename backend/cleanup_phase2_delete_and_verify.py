"""PHASE 2: DELETE matching records ONLY.
   Delete:
     - Users with role!=ADMIN matching uid list from phase1
     - Linked profiles for those uids
     - OTPs for the target phone (temporary sessions)
   NO other data (colleges, cutoffs, other users) is touched.
"""
import os
import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.auth_service import normalize_phone

TARGET_EMAIL = "rajputshrinath349@gmail.com"
TARGET_EMAIL_NORM = TARGET_EMAIL.strip().lower()
TARGET_PHONE_RAW = "9699510445"

PLAN_FILE = Path(__file__).parent / "_cleanup_plan.json"


async def main():
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")

    try:
        target_phone_norm = normalize_phone(TARGET_PHONE_RAW)
    except Exception:
        target_phone_norm = None

    if PLAN_FILE.exists():
        with open(PLAN_FILE, "r") as f:
            plan = json.load(f)
        uids = plan.get("uids_to_delete", [])
    else:
        uids = ["phone-+919699510445", "Cx8WUeN9BXaBov0DLZgndEGpJh03"]

    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    await client.admin.command("ping")

    db = client[db_name]
    users = db["users"]
    profiles = db["profiles"]
    otps = db["otps"]

    print("=" * 80)
    print("PHASE 2: DELETING MATCHING RECORDS ONLY")
    print("=" * 80)
    print(f"Database: {db_name}")
    print(f"Target email normalized: {TARGET_EMAIL_NORM}")
    print(f"Target phone normalized: {target_phone_norm}")
    print(f"UIDs to delete: {len(uids)}")
    for u in uids:
        print(f"  -> {u}")
    print()

    total_users_deleted = 0
    total_profiles_deleted = 0
    total_otps_deleted = 0
    deleted_user_ids = []

    for uid in uids:
        # Find user first, ensure role != ADMIN
        u_doc = await users.find_one({"uid": uid})
        if not u_doc:
            print(f"[SKIP] user uid={uid} not found in `users`")
            continue
        if u_doc.get("role") == "ADMIN":
            print(f"[SKIP] user uid={uid} IS ADMIN (role=ADMIN). WILL NOT DELETE.")
            continue
        # Delete the user
        result_u = await users.delete_one({"uid": uid, "role": {"$ne": "ADMIN"}})
        if result_u.deleted_count > 0:
            total_users_deleted += 1
            deleted_user_ids.append(uid)
            print(f"[DELETE users] uid={uid} OK ({result_u.deleted_count} doc)")

        # Delete linked profile
        result_p = await profiles.delete_one({"uid": uid})
        if result_p.deleted_count > 0:
            total_profiles_deleted += result_p.deleted_count
            print(f"[DELETE profiles] uid={uid} OK ({result_p.deleted_count} doc)")

    # Clean OTP sessions for the target phone (temporary, safe)
    if target_phone_norm:
        result_o = await otps.delete_many({"phone": target_phone_norm})
        total_otps_deleted += result_o.deleted_count
        if result_o.deleted_count > 0:
            print(f"[DELETE otps] phone={target_phone_norm} OK ({result_o.deleted_count} session(s))")

    print()
    print("-" * 80)
    print("DELETION SUMMARY")
    print("-" * 80)
    print(f"  users    deleted: {total_users_deleted}")
    print(f"  profiles deleted: {total_profiles_deleted}")
    print(f"  otps     deleted: {total_otps_deleted}")
    print(f"  uids cleared     : {deleted_user_ids}")
    print()

    # PHASE 3: VERIFY DELETION
    print("=" * 80)
    print("PHASE 3: VERIFICATION — Query again to ensure email/phone are GONE")
    print("=" * 80)

    all_users = await users.find({}).to_list(length=50000)

    email_hits = []
    phone_hits = []
    for u in all_users:
        stored_email = u.get("email")
        if (
            stored_email
            and isinstance(stored_email, str)
            and stored_email.strip().lower() == TARGET_EMAIL_NORM
        ):
            email_hits.append({"_id": str(u.get("_id")), "uid": u.get("uid"), "email": stored_email})

        stored_phone = u.get("phone")
        if stored_phone and isinstance(stored_phone, str) and target_phone_norm:
            try:
                if normalize_phone(stored_phone) == target_phone_norm:
                    phone_hits.append(
                        {"_id": str(u.get("_id")), "uid": u.get("uid"), "phone": stored_phone}
                    )
            except Exception:
                if stored_phone == TARGET_PHONE_RAW:
                    phone_hits.append(
                        {"_id": str(u.get("_id")), "uid": u.get("uid"), "phone": stored_phone}
                    )

    # Also check profiles (some may have phone via profile, not in user)
    profile_phone_hits = []
    profile_email_hits = []
    for uid in ["phone-+919699510445", "Cx8WUeN9BXaBov0DLZgndEGpJh03"]:
        p = await profiles.find_one({"uid": uid})
        if p:
            if p.get("email"):
                if p["email"].strip().lower() == TARGET_EMAIL_NORM:
                    profile_email_hits.append({"uid": uid, "profile_email": p.get("email")})
            if p.get("phone") and target_phone_norm:
                try:
                    if normalize_phone(p["phone"]) == target_phone_norm:
                        profile_phone_hits.append({"uid": uid, "profile_phone": p.get("phone")})
                except Exception:
                    pass

    print(f"\nEmail '{TARGET_EMAIL}' remaining in users: {len(email_hits)}")
    for h in email_hits:
        print(f"  REMAINING: {h}")
    print(f"Phone '{TARGET_PHONE_RAW}' remaining in users: {len(phone_hits)}")
    for h in phone_hits:
        print(f"  REMAINING: {h}")
    print(f"Profiles still present for deleted uids in profiles:")
    print(f"  email hits  : {len(profile_email_hits)}")
    print(f"  phone hits  : {len(profile_phone_hits)}")

    remaining_any = len(email_hits) + len(phone_hits) + len(profile_email_hits) + len(profile_phone_hits)

    print()
    print("-" * 80)
    if remaining_any == 0:
        print("✅ VERIFICATION PASSED: Email, Phone, and linked profiles NO LONGER exist in the database.")
    else:
        print(f"⚠️  VERIFICATION ISSUE: {remaining_any} leftover references found (see above).")

    try:
        await client.close()
    except Exception:
        pass

    # Cleanup the plan file
    if PLAN_FILE.exists():
        PLAN_FILE.unlink()


if __name__ == "__main__":
    asyncio.run(main())
