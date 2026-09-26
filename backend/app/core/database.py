import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

db = Database()

def get_db():
    return db.db

async def connect_to_mongo():
    try:
        kwargs = {"serverSelectionTimeoutMS": 5000}
        if "+srv" in settings.MONGODB_URI or "tls=true" in settings.MONGODB_URI.lower():
            try:
                import certifi
                kwargs["tls"] = True
                kwargs["tlsCAFile"] = certifi.where()
            except Exception:
                pass

        db.client = AsyncIOMotorClient(settings.MONGODB_URI, **kwargs)
        db.db = db.client[settings.MONGODB_DATABASE]
        await db.db["analytics_events"].create_index([("eventType", 1)])
        await db.db["analytics_events"].create_index([("userId", 1)])
        await db.db["analytics_events"].create_index([("collegeId", 1)])
        await db.db["analytics_events"].create_index([("timestamp", -1)])
        await db.db["users"].create_index([("role", 1)])
        await db.db["users"].create_index([("email", 1)], unique=False)
        masked_uri = settings.MONGODB_URI
        if "@" in masked_uri:
            masked_uri = "mongodb+srv://****@" + masked_uri.split("@", 1)[1]
        logger.info("Initialized MongoDB client at %s (database: %s)", masked_uri, settings.MONGODB_DATABASE)
    except Exception as e:
        logger.warning("MongoDB initialization warning: %s", e)

async def close_mongo_connection():
    """Cleanly close MongoDB client on application shutdown."""
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection")
        db.client = None
        db.db = None
