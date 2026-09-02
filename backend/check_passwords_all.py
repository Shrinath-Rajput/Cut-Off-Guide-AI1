import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import connect_to_mongo, get_db
from app.core.security import verify_password, get_password_hash
from passlib.context import CryptContext

async def check():
    await connect_to_mongo()
    db = get_db()
    users = await db["users"].find({}).to_list(length=100)
    for u in users:
        email = u.get("email")
        pw_hash = u.get("passwordHash")
        print(f"User: email={email}, role={u.get('role')}, has_hash={bool(pw_hash)}")
        if email == "ankitakenjale75@gmail.com":
            print("  Admin 'Ankita@123':", verify_password("Ankita@123", pw_hash))
        if email == "fourise@gmail.com":
            print("  SuperAdmin '123456':", verify_password("123456", pw_hash))
        if email == "sarthakpatil12@gmail.com":
            print("  Sarthak 'Sarthak@123':", verify_password("Sarthak@123", pw_hash))
            print("  Sarthak '123456':", verify_password("123456", pw_hash))
            print("  Sarthak 'sarthak12':", verify_password("sarthak12", pw_hash))

asyncio.run(check())
