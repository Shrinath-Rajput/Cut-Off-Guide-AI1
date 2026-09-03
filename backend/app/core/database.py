import asyncio
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

def get_db():
    return db.db

def _try_start_local_mongodb() -> bool:
    """If connecting to localhost fails, attempt to start local mongod pointing to project _mongodata."""
    try:
        mongod_path = shutil.which("mongod")
        if not mongod_path:
            import glob
            matches = glob.glob("C:/Program Files/MongoDB/Server/*/bin/mongod.exe")
            if matches:
                mongod_path = matches[0]
        if not mongod_path:
            logging.warning("Could not find mongod executable to start local MongoDB.")
            return False

        # Locate _mongodata
        possible_roots = [
            Path(__file__).resolve().parents[3],
            Path.cwd().parent,
            Path.cwd(),
        ]
        data_dir = None
        for root in possible_roots:
            candidate = root / "_mongodata"
            if candidate.exists() and candidate.is_dir():
                data_dir = candidate
                break

        if not data_dir:
            logging.warning("Could not locate _mongodata directory for MongoDB auto-start.")
            return False

        log_file = data_dir.parent / "backend" / "mongod-active.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.info("Auto-starting local MongoDB using %s (data: %s)...", mongod_path, data_dir)
        cmd = [
            str(mongod_path),
            "--dbpath", str(data_dir),
            "--bind_ip", "127.0.0.1",
            "--port", "27017"
        ]
        
        flags = 0
        if sys.platform == "win32":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)

        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags
        )
        return True
    except Exception as exc:
        logging.warning("Failed to auto-start local MongoDB: %s", exc)
        return False

async def connect_to_mongo(max_retries: int = 4, retry_delay: float = 1.5):
    client = None
    last_exception = None
    is_local = "localhost" in settings.MONGODB_URI or "127.0.0.1" in settings.MONGODB_URI
    started_daemon = False

    for attempt in range(1, max_retries + 1):
        try:
            client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=4000)
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

            if is_local and not started_daemon:
                started_daemon = _try_start_local_mongodb()
                if started_daemon:
                    await asyncio.sleep(2.0)
                    continue

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
