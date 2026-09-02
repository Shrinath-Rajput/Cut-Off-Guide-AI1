import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

def get_db():
    return db.db

async def connect_to_mongo(max_retries: int = 3, retry_delay: float = 1.0):
    client = None
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            database = client[settings.MONGODB_DATABASE]
            await client.admin.command("ping")
            await database["analytics_events"].create_index([("eventType", 1)])
            await database["analytics_events"].create_index([("userId", 1)])
            await database["analytics_events"].create_index([("collegeId", 1)])
            await database["analytics_events"].create_index([("timestamp", -1)])
            await database["users"].create_index([("role", 1)])
            await database["users"].create_index([("email", 1)], unique=False)
            await database["users"].create_index([("phone", 1)], unique=False)
            db.client = client
            db.db = database
            logging.info("Initialized MongoDB client at %s (database: %s)", settings.MONGODB_URI, settings.MONGODB_DATABASE)
            return
        except Exception as e:
            last_exception = e
            logging.warning("MongoDB connection attempt %d/%d failed: %s", attempt, max_retries, e)
            if client:
                client.close()
                client = None
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)

    db.client = None
    db.db = None
    raise RuntimeError("MongoDB initialization failed") from last_exception

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logging.info("Closed MongoDB connection")
        db.client = None
        db.db = None
