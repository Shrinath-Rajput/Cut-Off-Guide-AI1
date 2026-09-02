import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    dbs = await client.list_database_names()
    for db_name in dbs:
        db = client[db_name]
        cols = await db.list_collection_names()
        for col in cols:
            if "user" in col.lower():
                users = await db[col].find({}).to_list(length=100)
                print(f"\nDB: {db_name}, Collection: {col}, Count: {len(users)}")
                for u in users:
                    # print details safely
                    uid = u.get("uid") or u.get("_id")
                    email = u.get("email")
                    name = u.get("name") or u.get("username")
                    ph = u.get("passwordHash") or u.get("password_hash") or u.get("password") or u.get("hash")
                    salt = u.get("salt")
                    print(f"  User: email={email}, name={name}, uid={uid}, role={u.get('role')}")
                    print(f"    pw fields: has_ph={bool(ph)}, ph_type={type(ph).__name__}, salt={bool(salt)}")
                    if ph:
                        print(f"    ph value: {ph[:50] if isinstance(ph, str) else str(ph)[:50]}")
                    if salt:
                        print(f"    salt value: {salt[:50] if isinstance(salt, str) else str(salt)[:50]}")

asyncio.run(check())
