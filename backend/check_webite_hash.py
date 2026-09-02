import asyncio
import hashlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    webite_users = await client["webite"]["users"].find({}).to_list(length=100)
    
    password = "Shrinath@123456"
    
    for u in webite_users:
        if u.get("email") == "rajputshrinath349@gmail.com":
            stored_hash = u.get("hash")
            stored_salt = u.get("salt")
            print(f"Checking user {u.get('username')}: hash_len={len(stored_hash)}, salt_len={len(stored_salt)}")
            # passport-local-mongoose default:
            # crypto.pbkdf2(password, salt, 25000, 512, 'sha512') -> hex or 32 iterations
            for iters in [25000, 1000, 10000, 32, 1]:
                for keylen in [64, 512, 32, 128]:
                    for algo in ['sha512', 'sha256', 'sha1', 'md5']:
                        try:
                            salt_bytes = bytes.fromhex(stored_salt)
                            derived = hashlib.pbkdf2_hmac(algo, password.encode('utf-8'), salt_bytes, iters, keylen)
                            if derived.hex() == stored_hash:
                                print(f"MATCH FOUND in webite for {u.get('username')}! algo={algo}, iters={iters}, keylen={keylen}")
                            # Also try utf-8 salt
                            derived2 = hashlib.pbkdf2_hmac(algo, password.encode('utf-8'), stored_salt.encode('utf-8'), iters, keylen)
                            if derived2.hex() == stored_hash:
                                print(f"MATCH (utf8 salt) for {u.get('username')}! algo={algo}, iters={iters}, keylen={keylen}")
                        except Exception as e:
                            pass

asyncio.run(check())
