#!/usr/bin/env python3
"""
Deep diagnostic: Test password verification against actual stored hashes.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv()

# Connect to MongoDB and get hashes
try:
    import pymongo
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[os.getenv("MONGO_DB_NAME", "cutoffgrid")]
    db.command("ping")
    print(f"✓ Connected to MongoDB\n")
except Exception as e:
    print(f"✗ DB connection failed: {e}")
    sys.exit(1)

# Import password functions
from app.core.security import verify_password, get_password_hash

# Test users to investigate
target_users = [
    "testuser9134@cutoffgrid.dev",  # This one works
    "testuser7034@cutoffgrid.dev",  # This one works
    "rajputshrinath129@gmail.com",  # This supposedly works
    "rajputshrinath349@gmail.com",  # This doesn't work
]

test_passwords = [
    "Secure@TestPass123!",
    "password",
    "test",
    "Test@123",
    "Test@1234",
    "Secure@123",
]

print("=" * 80)
print("PASSWORD VERIFICATION DIAGNOSTIC")
print("=" * 80)

for email in target_users:
    print(f"\n{'-' * 80}")
    print(f"Email: {email}")
    print(f"{'-' * 80}")
    
    # Find user in MongoDB
    user = db["users"].find_one({"email": email})
    
    if not user:
        print(f"  ✗ User not found in database")
        continue
    
    print(f"  UID: {user.get('uid')}")
    print(f"  Provider: {user.get('provider')}")
    
    password_hash = user.get("passwordHash") or user.get("password_hash")
    legacy_password = user.get("password")
    
    if not password_hash and not legacy_password:
        print(f"  ✗ No password hash or legacy password found")
        continue
    
    if password_hash:
        print(f"  Has passwordHash: YES (bcrypt)")
        print(f"    Hash (first 40 chars): {password_hash[:40]}...")
        print(f"    Hash algorithm: {'bcrypt' if '$2' in password_hash else 'other'}")
        
        # Test verification against known passwords
        print(f"\n  Testing password verification:")
        for test_pwd in test_passwords:
            try:
                is_valid = verify_password(test_pwd, password_hash)
                status = "✓ VALID" if is_valid else "✗ invalid"
                print(f"    {status}: '{test_pwd}'")
                if is_valid:
                    print(f"      ^ This password works for {email}!")
            except Exception as e:
                print(f"    ERROR: {test_pwd} -> {e}")
    
    if legacy_password:
        print(f"  Has legacy password field: YES")
        print(f"    Value: {repr(legacy_password[:50])}")
        
        try:
            if verify_password("unused", legacy_password):
                print(f"    Note: Field appears to be a valid hash")
            else:
                print(f"    Note: Field appears to be plain text or incompatible hash")
        except:
            print(f"    Note: Field might be plain text (not a valid hash)")

print(f"\n{'=' * 80}")
print("HASH FORMAT ANALYSIS")
print(f"{'=' * 80}")

# Look at hash formats in database
all_users = db["users"].find({"provider": "password"})
hash_formats = {}
for user in all_users:
    h = user.get("passwordHash") or user.get("password_hash") or ""
    if h:
        # Extract format prefix
        if h.startswith("$2"):
            fmt = "bcrypt ($2)"
        elif h.startswith("$bcrypt"):
            fmt = "bcrypt-sha256 ($bcrypt)"
        elif h.startswith("$"):
            fmt = f"Other phc ({h.split('$')[1]})"
        else:
            fmt = "Plain text or unknown"
        
        hash_formats[fmt] = hash_formats.get(fmt, 0) + 1

print("\nHash format distribution among password providers:")
for fmt, count in sorted(hash_formats.items()):
    print(f"  {count:2d} users: {fmt}")

client.close()
