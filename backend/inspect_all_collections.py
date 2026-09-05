import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def inspect_all():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    dbs = await client.list_database_names()
    for db_name in dbs:
        db = client[db_name]
        cols = await db.list_collection_names()
        for col_name in cols:
            count = await db[col_name].count_documents({})
            if count < 50:
                docs = await db[col_name].find({}).to_list(length=50)
                print(f"\n==========================================")
                print(f"DB: {db_name}, Col: {col_name}, Count: {count}")
                print(f"==========================================")
                for d in docs:
                    # Clean ObjectId and datetime for printing
                    d_clean = {k: str(v) for k, v in d.items()}
                    print(d_clean)

asyncio.run(inspect_all())
