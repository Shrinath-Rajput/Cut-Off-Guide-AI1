import asyncio
import glob
import logging
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
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

def is_mongo_listening(host: str = "127.0.0.1", port: int = 27017, timeout: float = 0.25) -> bool:
    """Fast check whether MongoDB is actively accepting TCP socket connections."""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        db.db = db.client[settings.MONGODB_DATABASE]
        await db.db["analytics_events"].create_index([("eventType", 1)])
        await db.db["analytics_events"].create_index([("userId", 1)])
        await db.db["analytics_events"].create_index([("collegeId", 1)])
        await db.db["analytics_events"].create_index([("timestamp", -1)])
        await db.db["users"].create_index([("role", 1)])
        await db.db["users"].create_index([("email", 1)], unique=False)
        await db.db["users"].create_index([("phone", 1)], unique=False)
        logging.info("Initialized MongoDB client at %s", settings.MONGODB_URI)
    except Exception as e:
        logging.warning("MongoDB initialization warning: %s", e)

async def close_mongo_connection():
    """Cleanly close MongoDB client on application shutdown."""
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection")
        db.client = None
        db.db = None
