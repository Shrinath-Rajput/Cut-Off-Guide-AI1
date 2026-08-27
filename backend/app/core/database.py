import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

def get_db():
    return db.db

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=500)
        db.db = db.client[settings.MONGODB_DATABASE]
        logging.info("Initialized MongoDB client at %s", settings.MONGODB_URI)
    except Exception as e:
        logging.warning("MongoDB initialization warning: %s", e)

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logging.info("Closed MongoDB connection")
