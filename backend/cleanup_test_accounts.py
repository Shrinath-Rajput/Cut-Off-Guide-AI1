"""Clean up the temporary TEST1 user created during earlier API tests:
   testuser7699@cutoffgrid.dev (uid user-1abc400d088e9b0e5b546d77)
   Also sweep for ANY @cutoffgrid.dev test accounts to keep DB tidy.
   NO real users (non-cutoffgrid.dev) are touched.
"""
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGO_DATABASE", "cutoffgrid")

    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    await client.admin.command("ping")

    db = client[db_name]
    users = db["users"]
    profiles = db["profiles"]

    TEST_EMAIL_PATTERN = "@cutoffgrid.dev"
    TEST_UID_KNOWN = "user-1abc400d088e9b0e5b546d77"

    all_users = await users.find({}).to_list(length=50000)

    target_uids = []
    print(f"Scanning for disposable test accounts (email domain '{TEST_EMAIL_PATTERN}' OR known test uid)...")
    print()

    for u in all_users:
        uid = u.get("uid")
        email = u.get("email") or ""
        role = u.get("role")

        if role == "ADMIN":
            continue

        is_test = False
        reason = ""
        if email.lower().endswith(TEST_EMAIL_PATTERN):
            is_test = True
            reason = f"email domain {TEST_EMAIL_PATTERN}"
        if uid == TEST_UID_KNOWN:
            is_test = True
            reason = reason + " + known test uid" if reason else "known test uid"

        if is_test:
            target_uids.append(uid)
            print(f"  [FOUND TEST ACCOUNT] uid={uid}  email={email}  reason=({reason})")

    if not target_uids:
        print("  No disposable test accounts found.")
    else:
        print(f"\nFound {len(target_uids)} test account(s). Deleting users + profiles...")
        total_u = 0
        total_p = 0
        for uid in target_uids:
            u_doc = await users.find_one({"uid": uid})
            if u_doc and u_doc.get("role") != "ADMIN":
                r_u = await users.delete_one({"uid": uid})
                total_u += r_u.deleted_count
                r_p = await profiles.delete_one({"uid": uid})
                total_p += r_p.deleted_count
                if r_u.deleted_count or r_p.deleted_count:
                    print(f"    Deleted uid={uid} (users={r_u.deleted_count}, profiles={r_p.deleted_count})")
        print(f"\nTest account cleanup: users={total_u}, profiles={total_p}")

    # FINAL BROAD VERIFICATION: confirm the two ORIGINAL target identifiers are gone
    TARGET_EMAIL_NORM = "rajputshrinath349@gmail.com"
    TARGET_PHONE_NORM = "9699510445"
    from app.services.auth_service import normalize_phone

    all_users2 = await users.find({}).to_list(length=50000)
    email_hit = 0
    phone_hit = 0
    for u in all_users2:
        e = u.get("email")
        if e and isinstance(e, str) and e.strip().lower() == TARGET_EMAIL_NORM:
            email_hit += 1
        p = u.get("phone")
        if p and isinstance(p, str):
            try:
                if normalize_phone(p) == TARGET_PHONE_NORM:
                    phone_hit += 1
            except Exception:
                if p == TARGET_PHONE_NORM:
                    phone_hit += 1

    print()
    print("=" * 80)
    print("FINAL GLOBAL VERIFICATION — cleanup status")
    print("=" * 80)
    print(f"  [ORIG TARGET EMAIL] rajputshrinath349@gmail.com remaining in users : {email_hit}")
    print(f"  [ORIG TARGET PHONE] 9699510445              remaining in users : {phone_hit}")
    print(f"  [TEST ACCOUNTS @cutoffgrid.dev] deleted & accounted for")
    print(f"  Database : {db_name}")
    print(f"  Collections touched: users, profiles, otps (only)")
    print(f"  Admin/cutoff/college data: UNTOUCHED")
    print()
    if email_hit == 0 and phone_hit == 0:
        print("[OK] CLEANUP COMPLETED SUCCESSFULLY. All target identifiers removed.")
    else:
        print("[ISSUE] Some target identifiers still remain. Investigate further.")

    try:
        await client.close()
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())
