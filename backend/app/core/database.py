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
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def _find_mongod_executable() -> Optional[Path]:
    """Locate mongod.exe from PATH, environment, or standard Windows installation paths."""
    env_path = os.getenv("MONGOD_PATH")
    if env_path and Path(env_path).is_file():
        return Path(env_path)

    which_path = shutil.which("mongod")
    if which_path:
        return Path(which_path)

    search_patterns = [
        "C:/Program Files/MongoDB/Server/*/bin/mongod.exe",
        "C:/Program Files (x86)/MongoDB/Server/*/bin/mongod.exe",
        "C:/MongoDB/bin/mongod.exe",
        "D:/MongoDB/bin/mongod.exe",
    ]
    for pattern in search_patterns:
        matches = sorted(glob.glob(pattern), reverse=True)
        if matches:
            return Path(matches[0])

    return None

def _find_data_directory() -> Optional[Path]:
    """Locate the project _mongodata directory."""
    env_dir = os.getenv("MONGO_DATA_DIR")
    if env_dir and Path(env_dir).is_dir():
        return Path(env_dir)

    possible_roots = [
        Path(__file__).resolve().parents[3],
        Path(__file__).resolve().parents[2],
        Path.cwd(),
        Path.cwd().parent,
    ]

    for root in possible_roots:
        for candidate_name in ["_mongodata", "mongo_data"]:
            candidate = root / candidate_name
            if candidate.exists() and candidate.is_dir():
                return candidate

    return None

def ensure_local_mongodb_running(host: str = "127.0.0.1", port: int = 27017, max_wait_sec: float = 12.0) -> bool:
    """Ensure local MongoDB instance is up and listening on host:port.
    1. If already listening, returns True immediately (<1ms).
    2. If not listening, attempts Windows service start if elevated.
    3. If still not listening, launches local mongod daemon process.
    4. Polls port until available or timeout.
    """
    if is_mongo_listening(host, port):
        return True

    logger.info("MongoDB on %s:%d is not responding. Attempting auto-start...", host, port)

    # Step A: Attempt Windows Service start (works if user/service manager allows)
    if sys.platform == "win32":
        try:
            subprocess.run(["sc.exe", "start", "MongoDB"], capture_output=True, timeout=2)
            time.sleep(0.4)
            if is_mongo_listening(host, port):
                logger.info("MongoDB Windows Service started successfully.")
                return True
        except Exception:
            pass

    # Step B: Auto-start mongod executable using project _mongodata
    mongod_path = _find_mongod_executable()
    if not mongod_path:
        logger.error(
            "Could not locate mongod executable on this system. "
            "Please ensure MongoDB is installed or specify MONGOD_PATH environment variable."
        )
        return False

    data_dir = _find_data_directory()
    if not data_dir:
        logger.error("Could not locate project _mongodata directory for MongoDB auto-start.")
        return False

    log_file = data_dir.parent / "backend" / "mongod-active.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Auto-starting local MongoDB using %s (data: %s)...", mongod_path, data_dir)
    cmd = [
        str(mongod_path),
        "--dbpath", str(data_dir),
        "--bind_ip", host,
        "--port", str(port),
        "--wiredTigerCacheSizeGB", "0.5",
        "--logpath", str(log_file),
        "--logappend"
    ]

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            close_fds=True
        )
    except Exception as exc:
        logger.error("Failed to execute mongod process: %s", exc)
        return False

    # Poll port readiness with bounded timeout
    start_time = time.time()
    while time.time() - start_time < max_wait_sec:
        if is_mongo_listening(host, port, timeout=0.2):
            elapsed = time.time() - start_time
            logger.info("Local MongoDB became ready and listening in %.2fs", elapsed)
            return True
        time.sleep(0.15)

    logger.error("MongoDB did not become available on %s:%d within %.1fs", host, port, max_wait_sec)
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                recent_logs = "".join(lines[-10:])
                logger.error("Recent MongoDB logs:\n%s", recent_logs)
        except Exception:
            pass

    return False

async def connect_to_mongo(max_retries: int = 4, retry_delay: float = 1.0):
    """Initialize central MongoDB connection and create essential collection indexes."""
    client = None
    last_exception = None
    is_local = "localhost" in settings.MONGODB_URI or "127.0.0.1" in settings.MONGODB_URI

    # Early pre-flight check for local MongoDB
    if is_local:
        ensure_local_mongodb_running()

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
            logger.info("Initialized MongoDB client at %s (database: %s)", settings.MONGODB_URI, settings.MONGODB_DATABASE)
            return
        except Exception as e:
            last_exception = e
            logger.warning("MongoDB connection attempt %d/%d failed: %s", attempt, max_retries, e)
            if client:
                client.close()
                client = None

            if is_local:
                ensure_local_mongodb_running()

            if attempt < max_retries:
                await asyncio.sleep(retry_delay)

    db.client = None
    db.db = None
    raise RuntimeError("MongoDB initialization failed") from last_exception

async def close_mongo_connection():
    """Cleanly close MongoDB client on application shutdown."""
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection")
        db.client = None
        db.db = None
