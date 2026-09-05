import asyncio
import hashlib
import binascii
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def test():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    webite_users = await client["webite"]["users"].find({}).to_list(length=100)
    
    passwords = [
        "Shrinath@123456",
        "Shrinath@123",
        "shrinath@123456",
        "Shrinath123",
        "Shrinath123456",
        "Shrinath_Rajput",
        "rajputshrinath349",
        "123456",
        "12345678",
        "123456789",
        "student",
        "delta-student",
    ]
    
    for u in webite_users:
        stored_hash = u.get("hash")
        stored_salt = u.get("salt")
        username = u.get("username")
        email = u.get("email")
        if not stored_hash or not stored_salt:
            continue
        print(f"\nTesting user: username={username}, email={email}")
        
        # In passport-local-mongoose:
        # crypto.pbkdf2(password, salt, iterations, keylen, digest, callback)
        # default iterations: 25000, keylen: 512, digest: 'sha512'
        # or iterations: 32, keylen: 512, digest: 'sha1' (older passport-local-mongoose)
        # or salt as hex buffer vs string
        for pw in passwords:
            for iters in [25000, 32, 1000, 10000, 5000, 100, 1]:
                for digest in ['sha512', 'sha256', 'sha1', 'md5']:
                    # Try salt as hex bytes
                    try:
                        salt_bytes = bytes.fromhex(stored_salt)
                        h = hashlib.pbkdf2_hmac(digest, pw.encode('utf-8'), salt_bytes, iters, 512).hex()
                        if h == stored_hash:
                            print(f"  [MATCH!] pw='{pw}' with iters={iters}, digest={digest}, salt=hex")
                    except Exception:
                        pass
                    # Try salt as raw string bytes
                    try:
                        salt_raw = stored_salt.encode('utf-8')
                        h = hashlib.pbkdf2_hmac(digest, pw.encode('utf-8'), salt_raw, iters, 512).hex()
                        if h == stored_hash:
                            print(f"  [MATCH!] pw='{pw}' with iters={iters}, digest={digest}, salt=utf8")
                    except Exception:
                        pass

asyncio.run(test())
