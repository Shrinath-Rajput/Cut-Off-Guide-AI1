import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import connect_to_mongo, get_db
from app.core.security import verify_password

async def test():
    await connect_to_mongo()
    db = get_db()
    user = await db["users"].find_one({"email": "rajputshrinath349@gmail.com"})
    pw_hash = user.get("passwordHash")
    print("User email:", user.get("email"))
    print("User passwordHash:", pw_hash)
    print("LegacyPass@2026 match:", verify_password("LegacyPass@2026", pw_hash))

asyncio.run(test())
