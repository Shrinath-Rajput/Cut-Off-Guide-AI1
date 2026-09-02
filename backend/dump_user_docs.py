import asyncio
import hashlib
import binascii
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def test_hashes():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    # 1. Check all users in all databases
    dbs = await client.list_database_names()
    for db_name in dbs:
        db = client[db_name]
        for col_name in await db.list_collection_names():
            if "user" in col_name.lower():
                users = await db[col_name].find({}).to_list(length=100)
                for u in users:
                    if u.get("email") == "rajputshrinath349@gmail.com":
                        print(f"DB: {db_name}.{col_name} -> doc: {u}")

asyncio.run(test_hashes())
