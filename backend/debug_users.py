import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.auth_service import normalize_phone

async def inspect_db():
    print("=" * 80)
    print("MONGODB DIAGNOSTIC REPORT")
    print("=" * 80)
    
    print(f"\nMongoDB URI: {settings.MONGODB_URI}")
    print(f"Database: {settings.MONGODB_DATABASE}")
    
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    db = client[settings.MONGODB_DATABASE]
    
    # Check connection
    try:
        await client.admin.command('ping')
        print("\n[OK] MongoDB connection: SUCCESS")
    except Exception as e:
        print(f"\n[FAIL] MongoDB connection: FAILED - {e}")
        return
    
    # List collections
    collections = await db.list_collection_names()
    print(f"\nCollections: {collections}")
    
    # Check users collection
    if "users" in collections:
        users_count = await db["users"].count_documents({})
        print(f"\nTotal users: {users_count}")
        
        if users_count > 0:
            users = await db["users"].find({}).to_list(length=100)
            print(f"\n--- USER DOCUMENTS (first {len(users)} users) ---")
            for i, user in enumerate(users, 1):
                print(f"\nUser #{i}:")
                print(f"  _id: {user.get('_id')}")
                print(f"  uid: {user.get('uid')}")
                print(f"  name: {user.get('name')}")
                print(f"  email: {repr(user.get('email'))}")
                print(f"  phone: {repr(user.get('phone'))}")
                print(f"  provider: {user.get('provider')}")
                print(f"  role: {user.get('role')}")
                has_pw = user.get('passwordHash') or user.get('password_hash')
                print(f"  passwordHash present: {'Yes' if has_pw else 'NO'}")
                print(f"  createdAt: {user.get('createdAt')}")
                print(f"  lastLogin: {user.get('lastLogin')}")
    
    # Check profiles collection
    if "profiles" in collections:
        profiles_count = await db["profiles"].count_documents({})
        print(f"\nTotal profiles: {profiles_count}")
        if profiles_count > 0:
            profiles = await db["profiles"].find({}).to_list(length=50)
            print(f"\n--- PROFILE DOCUMENTS (first {len(profiles)} profiles) ---")
            for i, profile in enumerate(profiles, 1):
                print(f"\nProfile #{i}:")
                print(f"  _id: {profile.get('_id')}")
                print(f"  uid: {profile.get('uid')}")
                print(f"  name: {profile.get('name')}")
                print(f"  email: {repr(profile.get('email'))}")
                print(f"  phone: {repr(profile.get('phone'))}")
    
    # Check for normalization issues
    print("\n" + "=" * 80)
    print("NORMALIZATION CHECK")
    print("=" * 80)
    
    if "users" in collections and users_count > 0:
        print("\n--- Email normalization issues ---")
        emails_found = {}
        for user in users:
            email = user.get('email')
            if email:
                normalized = email.strip().lower()
                if normalized != email:
                    print(f"  [WARN] Email not normalized: uid={user.get('uid')}, email={repr(email)}, should be={repr(normalized)}")
                if normalized in emails_found:
                    print(f"  [WARN] DUPLICATE normalized email: {normalized}")
                    print(f"    - User 1: uid={emails_found[normalized]}")
                    print(f"    - User 2: uid={user.get('uid')}")
                else:
                    emails_found[normalized] = user.get('uid')
        
        print("\n--- Phone normalization issues ---")
        phones_found = {}
        for user in users:
            phone = user.get('phone')
            if phone:
                try:
                    normalized = normalize_phone(phone)
                    if normalized != phone:
                        print(f"  [WARN] Phone not normalized: uid={user.get('uid')}, phone={repr(phone)}, should be={repr(normalized)}")
                    if normalized in phones_found:
                        print(f"  [ERROR] DUPLICATE normalized phone: {normalized}")
                        print(f"    - User 1: uid={phones_found[normalized]}")
                        print(f"    - User 2: uid={user.get('uid')}")
                    else:
                        phones_found[normalized] = user.get('uid')
                except Exception as e:
                    print(f"  [WARN] Phone invalid: uid={user.get('uid')}, phone={repr(phone)}, error={e}")
    
    # Simulate duplicate check like register endpoint
    print("\n" + "=" * 80)
    print("SIMULATE REGISTER DUPLICATE CHECK (as per current code)")
    print("=" * 80)
    
    test_cases = [
        {"email": "test@example.com", "phone": "9876543210", "desc": "Brand new user"},
    ]
    
    # Add existing users to test
    if "users" in collections and users_count > 0:
        for user in users[:3]:
            email = user.get('email')
            phone = user.get('phone')
            if email and phone:
                test_cases.append({"email": email, "phone": phone, "desc": f"Existing user uid={user.get('uid')}"})
                # Swap to detect cross-field issues
                test_cases.append({"email": email + "_NEW", "phone": phone, "desc": f"New email, existing phone uid={user.get('uid')}"})
                test_cases.append({"email": email, "phone": "9999999999", "desc": f"Existing email, new phone uid={user.get('uid')}"})
    
    for tc in test_cases:
        print(f"\nTest case: {tc['desc']}")
        print(f"  email={repr(tc['email'])}, phone={repr(tc['phone'])}")
        
        email_norm = tc['email'].strip().lower()
        try:
            phone_norm = "".join(c for c in tc['phone'] if c.isdigit())[-10:]
        except:
            phone_norm = tc['phone']
        
        print(f"  normalized email={repr(email_norm)}, normalized phone={repr(phone_norm)}")
        
        existing_email = await db["users"].find_one({"email": email_norm})
        existing_phone = await db["users"].find_one({"phone": phone_norm})
        
        print(f"  Email check ({{'email': {repr(email_norm)}}}): {'FOUND CONFLICT' if existing_email else 'OK'}")
        if existing_email:
            print(f"    -> Conflicts with uid={existing_email.get('uid')}, stored_email={repr(existing_email.get('email'))}")
        
        print(f"  Phone check ({{'phone': {repr(phone_norm)}}}): {'FOUND CONFLICT' if existing_phone else 'OK'}")
        if existing_phone:
            print(f"    -> Conflicts with uid={existing_phone.get('uid')}, stored_phone={repr(existing_phone.get('phone'))}")
    
    print("\n" + "=" * 80)
    print("END OF DIAGNOSTIC REPORT")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_db())
