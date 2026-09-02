import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv()
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    print("ALL DATABASES:")
    dbs = await client.list_database_names()
    for db_name in dbs:
        print(f"\n=== Database: {db_name} ===")
        db = client[db_name]
        cols = await db.list_collection_names()
        for col in cols:
            count = await db[col].count_documents({})
            print(f"  Collection: {col} ({count} docs)")
            if col == "users" and count > 0:
                users = await db[col].find({}).to_list(length=200)
                for i, u in enumerate(users, 1):
                    fields = sorted(u.keys())
                    pw_hash = u.get("passwordHash") or u.get("password_hash") or u.get("password")
                    print(f"    User{i}: _id={u.get('_id')}")
                    print(f"      uid={u.get('uid')}")
                    print(f"      role={u.get('role')}")
                    print(f"      email={repr(u.get('email'))}")
                    print(f"      phone={repr(u.get('phone'))}")
                    print(f"      username={repr(u.get('username'))}")
                    print(f"      provider={u.get('provider')}")
                    print(f"      has_pw={'YES' if pw_hash else 'NONE'}")
                    if pw_hash and isinstance(pw_hash, str):
                        print(f"      pw_field={'passwordHash' if u.get('passwordHash') else ('password_hash' if u.get('password_hash') else 'password')}")
                        print(f"      pw_prefix={pw_hash[:20] if len(pw_hash) >= 20 else pw_hash}")
                    print(f"      all_fields={fields}")
    client.close()

asyncio.run(check())
