#!/usr/bin/env python3
"""
Inspect MongoDB users to understand password field state.
This helps diagnose why only one user works for authentication.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    print(f"Warning: .env file not found at {env_file}")

# Connect to MongoDB
try:
    import pymongo
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[os.getenv("MONGO_DB_NAME", "cutoffgrid")]
    
    # Test connection
    db.command("ping")
    print(f"✓ Connected to MongoDB at {mongo_uri}\n")
except Exception as e:
    print(f"✗ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Get all users
try:
    users = list(db["users"].find({}))
    print(f"Found {len(users)} user(s) in database:\n")
    
    for i, user in enumerate(users, 1):
        uid = user.get("uid", "NO_UID")
        email = user.get("email", "NO_EMAIL")
        phone = user.get("phone", "NO_PHONE")
        provider = user.get("provider", "NO_PROVIDER")
        
        # Check password fields
        has_password_hash = bool(user.get("passwordHash") or user.get("password_hash"))
        legacy_password = user.get("password")
        
        print(f"User #{i}")
        print(f"  UID:              {uid}")
        print(f"  Email:            {email}")
        print(f"  Phone:            {phone}")
        print(f"  Provider:         {provider}")
        print(f"  Has passwordHash: {has_password_hash}")
        if has_password_hash:
            hash_val = user.get("passwordHash") or user.get("password_hash")
            print(f"    Hash preview:  {hash_val[:30]}...")
        print(f"  Has legacy password: {bool(legacy_password)}")
        if legacy_password:
            print(f"    Value:         {repr(legacy_password[:50])}")
        print()

except Exception as e:
    print(f"✗ Error querying users: {e}")
    import traceback
    traceback.print_exc()

finally:
    client.close()
