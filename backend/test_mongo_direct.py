import sys
sys.path.insert(0, r"D:\e drive\old data 1 E drive\Fourise Project\Cut_off_Guide\backend")

import asyncio
from app.core.database import connect_to_mongo, get_db

async def test_motor():
    print("=== Testing Motor (async) MongoDB connection ===")
    try:
        await connect_to_mongo()
        print("CONNECTED via Motor successfully")
        db = get_db()
        db_name = db.name if db is not None else "None"
        print("DB name: %s" % db_name)
        
        result1 = await db["users"].find_one({"role": "SUPER_ADMIN"})
        print("find_one SUPER_ADMIN: %s" % (result1 is not None))
        
        all_users = await db["users"].find({}).to_list(length=10000)
        print("find ALL users to_list success, count: %d" % len(all_users))
        
        for u in all_users:
            has_pw = bool(u.get("passwordHash") or u.get("password_hash"))
            print("  USER: uid=%s role=%s email=%s has_pw_hash=%s" % (
                u.get("uid"), u.get("role"), u.get("email"), has_pw
            ))
        
    except Exception as e:
        import traceback
        print("MOTOR ERROR: %s: %s" % (type(e).__name__, e))
        traceback.print_exc()

def test_sync_config():
    print("")
    print("=== Testing root config.py sync MongoClient ===")
    try:
        import config
        client = config.get_mongo_client()
        print("Sync client object: %s" % client)
        if client is None:
            print("Sync client is NONE (connection failed at init)")
        else:
            db = config.get_db()
            print("Sync DB name: %s" % db.name)
            col = config.get_users_collection()
            print("Sync collection: %s" % col.name)
            count = col.count_documents({})
            print("Sync user count: %d" % count)
    except Exception as e:
        import traceback
        print("SYNC CONFIG ERROR: %s: %s" % (type(e).__name__, e))
        traceback.print_exc()

asyncio.run(test_motor())
test_sync_config()
