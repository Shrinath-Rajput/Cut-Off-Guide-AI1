"""
SAFE USER+AUTH DATA CLEANUP SCRIPT for CutoffGuideAI MongoDB.

RULES (STRICT):
  - DELETE ONLY:  users  |  profiles  |  otps  |  saved
  - KEEP INTACT:  colleges, cutoffs, admin_*, courses, branches, results,
                  enquiries, subscriptions, images, trainings, assistants,
                  chat histories, and any other application/reference data.
  - NEVER print:  passwords, passwordHash, OTP values, JWTs, secrets, keys.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "cutoffgrid"

# ------------------------------------------------------------------
# Collections classification
# ------------------------------------------------------------------
DELETE_COLLECTIONS = {
    "users": "Registered user accounts (uid, email, phone, name, provider, role)",
    "profiles": "User onboarding/profile data (linked via uid -> users.uid)",
    "otps": "Login/Signup OTP session records (linked via phone/session_id)",
    "saved": "User saved-college bookmarks (linked via uid -> users.uid)",
}

PROTECTED_COLLECTIONS_HINTS = [
    "colleges",
    "cutoffs",
    "courses",
    "branches",
    "results",
    "enquiries",
    "subscriptions",
    "images",
    "admincolleges",
    "admin_cutoffs",
    "admin_users",
    "contacts",
    "assistants",
    "chats",
    "trainings",
]


async def main():
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    try:
        await client.admin.command("ping")
        print(f"[OK] Connected to MongoDB at {MONGO_URI}")
    except Exception as exc:
        print(f"[FATAL] Cannot connect to MongoDB: {exc}")
        sys.exit(1)

    db = client[DB_NAME]

    # 1. Discover all collections currently in the database.
    print("\n" + "=" * 78)
    print(f"DISCOVERY: All collections in database '{DB_NAME}'")
    print("=" * 78)
    all_collection_names = await db.list_collection_names()
    all_collection_names.sort()

    counts = {}
    for cname in all_collection_names:
        try:
            counts[cname] = await db[cname].estimated_document_count()
        except Exception:
            counts[cname] = -1

    for cname in all_collection_names:
        marker = (
            "  [DELETE]" if cname in DELETE_COLLECTIONS
            else "  [KEEP  ]"
        )
        count_str = f"{counts[cname]:>8} docs" if counts[cname] >= 0 else "   unknown"
        reason = DELETE_COLLECTIONS.get(cname, "Application/reference data")
        print(f"  {marker}  {cname:<30s}  {count_str}   ({reason})")

    # 2. Summarize impact.
    print("\n" + "=" * 78)
    print("IMPACT SUMMARY (BEFORE)")
    print("=" * 78)
    delete_counts = {c: counts.get(c, 0) for c in DELETE_COLLECTIONS}
    for c, desc in DELETE_COLLECTIONS.items():
        n = delete_counts[c]
        print(f"  Will delete {n:>6d} doc(s) from '{c}'  ({desc})")

    protected_keep_count = sum(
        n for c, n in counts.items() if c not in DELETE_COLLECTIONS and n >= 0
    )
    protected_listed = [c for c in PROTECTED_COLLECTIONS_HINTS if c in counts]
    print(
        f"\n  Will keep ALL {len([c for c in counts if c not in DELETE_COLLECTIONS])}"
        f" non-user collections ({protected_keep_count} total docs preserved)."
    )
    if protected_listed:
        print(f"  Protected reference collections detected: {protected_listed}")

    # 3. Final guard — refuse if any protected hint collection would be deleted.
    bad = [c for c in PROTECTED_COLLECTIONS_HINTS if c in DELETE_COLLECTIONS]
    if bad:
        print(f"\n[ABORT] Misconfiguration — protected collections marked for delete: {bad}")
        sys.exit(2)

    # 4. Execute deletes.
    print("\n" + "=" * 78)
    print("EXECUTING SAFE DELETE OF USER+AUTH COLLECTIONS ONLY")
    print("=" * 78)
    results = {}
    for cname in DELETE_COLLECTIONS:
        if cname not in all_collection_names:
            results[cname] = 0
            print(f"  [SKIP] '{cname}' — collection does not exist")
            continue
        try:
            delete_result = await db[cname].delete_many({})
            results[cname] = delete_result.deleted_count
            print(f"  [DONE] Deleted {delete_result.deleted_count:>6d} doc(s) from '{cname}'")
        except Exception as exc:
            print(f"  [ERROR] Failed to delete from '{cname}': {exc}")
            results[cname] = None

    # 5. Final verification.
    print("\n" + "=" * 78)
    print("VERIFICATION (AFTER DELETE)")
    print("=" * 78)
    verify_ok = True
    all_collection_names_after = await db.list_collection_names()
    for cname in DELETE_COLLECTIONS:
        after_n = 0
        if cname in all_collection_names_after:
            try:
                after_n = await db[cname].estimated_document_count()
            except Exception:
                after_n = -1
        status = "PASS" if after_n == 0 else ("FAIL" if after_n > 0 else "UNKNOWN")
        if status != "PASS":
            verify_ok = False
        print(f"  [{status}] '{cname}': {after_n} doc(s) remaining  (expected 0)")

    # 6. Confirm protected data untouched.
    print("\n  Protected data counts (before -> after):")
    protected_verified = True
    for cname in PROTECTED_COLLECTIONS_HINTS:
        if cname not in all_collection_names:
            continue
        before_n = counts.get(cname, -1)
        after_n = -1
        if cname in all_collection_names_after:
            try:
                after_n = await db[cname].estimated_document_count()
            except Exception:
                after_n = -1
        status = "OK  " if before_n == after_n and after_n >= 0 else "WARN"
        if before_n != after_n:
            protected_verified = False
        print(
            f"    [{status}] {cname:<25s}:  before={str(before_n):>7s}   "
            f"after={str(after_n):>7s}"
        )

    # 7. Final verdict.
    print("\n" + "=" * 78)
    if verify_ok:
        print("✅ FINAL RESULT: ALL user/auth collections EMPTY.")
        print("   Users: 0   Profiles: 0   OTPs: 0   Saved: 0")
    else:
        print("❌ FINAL RESULT: Some user/auth collections still have documents!")
    if protected_verified:
        print("✅ Protected application/reference data: UNTOUCHED.")
    else:
        print("⚠️  Protected data may have changed — inspect the WARN rows above.")
    print("=" * 78)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
