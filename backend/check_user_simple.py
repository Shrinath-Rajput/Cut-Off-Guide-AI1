import os
import sys
import asyncio
from pathlib import Path

TARGET_EMAIL = "rajputshrinath349@gmail.com"
TARGET_EMAIL_NORM = TARGET_EMAIL.strip().lower()


def mask(v):
    if v is None:
        return "NULL"
    if not isinstance(v, str):
        return str(v)
    if len(v) <= 4:
        return "*" * len(v)
    return v[:2] + "*" * (len(v) - 4) + v[-2:]


async def main():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
    except ImportError:
        print("[IMPORT] Trying pymongo instead of motor")
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        try:
            client.admin.command("ping")
            print("[OK] DB connected (pymongo sync)")
        except Exception as e:
            print(f"[FAIL] DB connect error: {e}")
            return
        db = client["cutoffgrid"]
        users = db["users"]
        profiles = db["profiles"]
        all_users = list(users.find({}))
        do_work(all_users, users, profiles)
        return

    client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command("ping")
        print("[OK] DB connected (motor async)")
    except Exception as e:
        print(f"[FAIL] DB connect error: {e}")
        return

    db = client["cutoffgrid"]
    users = db["users"]
    profiles = db["profiles"]
    all_users = await users.find({}).to_list(length=10000)
    do_work(all_users, users, profiles, asyncio_run=True)


def do_work(all_users, users, profiles, asyncio_run=False):
    print(f"\n[INFO] Total users in DB: {len(all_users)}")
    print("\n" + "=" * 80)
    print(f"SEARCHING USERS FOR EMAIL (case-insensitive, strip): {TARGET_EMAIL}")
    print("=" * 80)

    for idx, u in enumerate(all_users, 1):
        stored_email = u.get("email")
        stored_email_norm = None
        matches = False
        if stored_email and isinstance(stored_email, str):
            stored_email_norm = stored_email.strip().lower()
            matches = stored_email_norm == TARGET_EMAIL_NORM
        print(f"\nUser #{idx}:")
        print(f"  uid              : {u.get('uid')}")
        print(f"  name             : {u.get('name')}")
        print(f"  email (raw)      : {repr(stored_email)}")
        print(f"  email (norm)     : {repr(stored_email_norm)}")
        print(f"  email matches tgt: {'YES' if matches else 'NO'}")
        print(f"  phone (raw)      : {repr(u.get('phone'))}")
        print(f"  role             : {u.get('role')}")
        print(f"  provider         : {u.get('provider')}")
        has_ph = bool(u.get("passwordHash") or u.get("password_hash") or u.get("password"))
        print(f"  has password     : {'YES' if has_ph else 'NO'} (hash value masked)")
        other_keys = [k for k in u.keys() if k not in {"_id", "uid", "name", "email", "phone", "provider", "role", "passwordHash", "password_hash", "password", "createdAt", "lastLogin"}]
        print(f"  other fields     : {other_keys}")


if __name__ == "__main__":
    asyncio.run(main())
