import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import connect_to_mongo, get_db
from app.core.security import verify_password, create_access_token

async def test():
    await connect_to_mongo()
    db = get_db()
    user = await db["users"].find_one({"email": "rajputshrinath349@gmail.com"})
    print("Found user:", user["uid"], user["email"], user["role"])
    pw_hash = user.get("passwordHash")
    print("Has passwordHash:", bool(pw_hash))
    
    # Test Shrinath@12345
    match = verify_password("Shrinath@12345", pw_hash)
    print("Match for 'Shrinath@12345':", match)

asyncio.run(test())
