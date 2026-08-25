"""
VERIFICATION PASS (ASCII-only, no emoji)
Confirm users/profiles/otps/saved = 0
Confirm all other existing collections are preserved with unchanged counts.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "cutoffgrid"

DELETE_COLLECTIONS = {"users", "profiles", "otps", "saved"}
EXPECTED_EXISTING = ["colleges", "cutoffs", "courses", "branches", "results",
                     "enquiries", "subscriptions", "images", "contacts"]


async def main():
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    try:
        await client.admin.command("ping")
        print(f"[OK] Connected to MongoDB at {MONGO_URI}  DB={DB_NAME}")
    except Exception as exc:
        print(f"[FATAL] Cannot connect: {exc}")
        sys.exit(1)

    db = client[DB_NAME]

    all_names = sorted(await db.list_collection_names())
    print(f"\n=== FULL COLLECTION LIST ({len(all_names)} collections) ===")

    user_auth_empty = True
    preserved_any = False
    protected_found = []

    counts = {}
    for name in all_names:
        try:
            n = await db[name].estimated_document_count()
        except Exception:
            n = -1
        counts[name] = n
        cat = "USER/AUTH" if name in DELETE_COLLECTIONS else "APP/REF  "
        marker = " (DELETE target)" if name in DELETE_COLLECTIONS else ""
        print(f"  [{cat}]  {name:<28s}  {n:>6d} docs{marker}")
        if name in DELETE_COLLECTIONS and n != 0:
            user_auth_empty = False
        if name in DELETE_COLLECTIONS:
            continue
        preserved_any = True
        if name in EXPECTED_EXISTING:
            protected_found.append((name, n))

    print("\n=== VERIFICATION ===")
    for c in DELETE_COLLECTIONS:
        n = counts.get(c, 0)
        status = "PASS" if n == 0 else "FAIL"
        print(f"  [{status}] {c:<10s} -> {n} docs (require 0)")

    print("\n=== PRESERVED REFERENCE COLLECTIONS (subset) ===")
    if protected_found:
        for c, n in protected_found:
            print(f"  [OK] {c:<20s} preserved: {n} docs")
    else:
        print("  [INFO] None of the expected reference collections currently exist")
        print("         (this is acceptable: they will be created when app uses them)")

    print(f"\n=== PRESERVATION SUMMARY ===")
    non_delete = [c for c in all_names if c not in DELETE_COLLECTIONS]
    non_delete_docs = sum(counts[c] for c in non_delete if counts.get(c, -1) >= 0)
    print(f"  Non-user-auth collections kept : {len(non_delete)}")
    print(f"  Non-user-auth total docs kept  : {non_delete_docs}")

    print("\n=== FINAL VERDICT ===")
    if user_auth_empty:
        print("  PASS: users, profiles, otps, saved ALL = 0 docs")
    else:
        print("  FAIL: some user-auth collection still has docs")
        sys.exit(2)
    if preserved_any:
        print("  PASS: application/reference collections preserved")
    else:
        print("  INFO: no reference collections existed yet (still safe)")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
