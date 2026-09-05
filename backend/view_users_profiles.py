import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client["cutoffgrid"]
    for u in await db["users"].find({}).to_list(length=10):
        print("USER:", u)
    for p in await db["profiles"].find({}).to_list(length=10):
        print("PROFILE:", p)

asyncio.run(main())
