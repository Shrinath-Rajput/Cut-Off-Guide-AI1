import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "cutoff_db")
MONGO_CONNECT_TIMEOUT_MS = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "10000"))

_client = None


def get_mongo_client():
    global _client

    if _client is not None:
        return _client

    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=MONGO_CONNECT_TIMEOUT_MS,
        )
        client.admin.command("ping")
    except ConnectionFailure as exc:
        logging.warning("MongoDB unavailable, continuing without persistence: %s", exc)
        return None

    _client = client
    logging.info("Connected to MongoDB database %s", DATABASE_NAME)
    return _client


def get_db():
    client = get_mongo_client()
    if client is None:
        return None
    return client[DATABASE_NAME]


def get_users_collection():
    db = get_db()
    if db is None:
        return None
    return db["users"]
