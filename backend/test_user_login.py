import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import connect_to_mongo, get_db
from app.core.security import verify_password
from app.core.config import settings

async def main():
    await connect_to_mongo()
    db = get_db()
    user = await db["users"].find_one({"email": "rajputshrinath349@gmail.com"})
    print("Found user:", user)
    if user:
        stored_hash = user.get("passwordHash") or user.get("password_hash") or user.get("password")
        print("Stored hash:", stored_hash)
        
        test_passwords = [
            "Shrinath@123456",
            "Shrinath@123456 ".strip(),
            "shrinath@123456",
            "123456",
            "Admin@123",
            "Ankita@123"
        ]
        for p in test_passwords:
            match = verify_password(p, stored_hash)
            print(f"Password '{p}': match={match}")

asyncio.run(main())
