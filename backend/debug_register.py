import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def inspect_indexes_and_test():
    print("=" * 80)
    print("MONGODB INDEXES + REGISTER ENDPOINT TEST")
    print("=" * 80)
    
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
    db = client[settings.MONGODB_DATABASE]
    
    print(f"\nDatabase: {settings.MONGODB_DATABASE}")
    
    # Check indexes on users collection
    print("\n" + "-" * 80)
    print("MONGODB INDEXES ON 'users' COLLECTION:")
    print("-" * 80)
    
    try:
        indexes = await db["users"].list_indexes().to_list(length=100)
        for idx in indexes:
            print(f"\nIndex name: {idx.get('name')}")
            print(f"  Key: {idx.get('key')}")
            print(f"  Unique: {idx.get('unique', False)}")
            print(f"  Sparse: {idx.get('sparse', False)}")
            print(f"  Background: {idx.get('background', False)}")
    except Exception as e:
        print(f"Error getting indexes: {e}")
    
    # Check indexes on profiles collection
    print("\n" + "-" * 80)
    print("MONGODB INDEXES ON 'profiles' COLLECTION:")
    print("-" * 80)
    
    try:
        indexes = await db["profiles"].list_indexes().to_list(length=100)
        for idx in indexes:
            print(f"\nIndex name: {idx.get('name')}")
            print(f"  Key: {idx.get('key')}")
            print(f"  Unique: {idx.get('unique', False)}")
    except Exception as e:
        print(f"Error getting indexes: {e}")
    
    # Test duplicate scenarios with actual insert attempts
    print("\n" + "-" * 80)
    print("TESTING DIRECT MONGO INSERT SCENARIOS:")
    print("-" * 80)
    
    import secrets
    from datetime import datetime, timezone
    from app.core.security import get_password_hash
    
    test_runs = []
    
    # Test 1: Completely new user
    uid1 = f"test-{secrets.token_hex(8)}"
    user1 = {
        "uid": uid1,
        "name": "Test User 1",
        "email": f"test1-{secrets.token_hex(6)}@example.com",
        "phone": f"9{secrets.token_hex(5)[1:]}",  # Random 10-digit starting with 9
        "provider": "password",
        "role": "USER",
        "passwordHash": get_password_hash("Test@123"),
        "createdAt": datetime.now(timezone.utc),
        "lastLogin": datetime.now(timezone.utc),
    }
    test_runs.append(("New unique user", user1))
    
    # Test 2: Try to insert same email again (will do after Test 1 insert)
    # Test 3: Try to insert same phone again (will do after Test 1 insert)
    
    for desc, user_doc in test_runs:
        print(f"\nTest: {desc}")
        print(f"  email={repr(user_doc['email'])}, phone={repr(user_doc['phone'])}")
        try:
            result = await db["users"].insert_one(user_doc)
            print(f"  [OK] Inserted successfully. _id={result.inserted_id}")
            
            # Now test duplicate email
            user_same_email = {
                "uid": f"test-{secrets.token_hex(8)}",
                "name": "Test Same Email",
                "email": user_doc['email'],  # Same email!
                "phone": f"8{secrets.token_hex(5)[1:]}",  # Different phone
                "provider": "password",
                "role": "USER",
                "passwordHash": get_password_hash("Test@123"),
                "createdAt": datetime.now(timezone.utc),
                "lastLogin": datetime.now(timezone.utc),
            }
            try:
                result2 = await db["users"].insert_one(user_same_email)
                print(f"  [FAIL] Same email inserted AGAIN without error! _id={result2.inserted_id}")
                print(f"  -> This means NO unique index on email.")
                # Clean up the duplicate we just created
                await db["users"].delete_one({"_id": result2.inserted_id})
            except Exception as e:
                print(f"  [OK] Same email correctly blocked: {e}")
            
            # Now test duplicate phone
            user_same_phone = {
                "uid": f"test-{secrets.token_hex(8)}",
                "name": "Test Same Phone",
                "email": f"different-{secrets.token_hex(6)}@example.com",  # Different email
                "phone": user_doc['phone'],  # Same phone!
                "provider": "password",
                "role": "USER",
                "passwordHash": get_password_hash("Test@123"),
                "createdAt": datetime.now(timezone.utc),
                "lastLogin": datetime.now(timezone.utc),
            }
            try:
                result3 = await db["users"].insert_one(user_same_phone)
                print(f"  [FAIL] Same phone inserted AGAIN without error! _id={result3.inserted_id}")
                print(f"  -> This means NO unique index on phone.")
                # Clean up
                await db["users"].delete_one({"_id": result3.inserted_id})
            except Exception as e:
                print(f"  [OK] Same phone correctly blocked: {e}")
            
            # Clean up test user 1
            await db["users"].delete_one({"_id": result.inserted_id})
            
        except Exception as e:
            print(f"  [ERROR] Initial insert failed: {e}")
    
    # Now let's test the ACTUAL register endpoint using FastAPI TestClient
    print("\n" + "-" * 80)
    print("TESTING ACTUAL /api/auth/register ENDPOINT:")
    print("-" * 80)
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        unique_tag = secrets.token_hex(5)
        
        # TEST A: Completely new registration
        test_a_email = f"api-test-{unique_tag}@example.com"
        test_a_phone = f"7{unique_tag[:9]}"
        if len(test_a_phone) < 10:
            test_a_phone = test_a_phone + "0" * (10 - len(test_a_phone))
        
        print(f"\nTest A: Register new user")
        print(f"  email={repr(test_a_email)}, phone={repr(test_a_phone)}")
        payload_a = {
            "name": "API Test User A",
            "email": test_a_email,
            "phone": test_a_phone,
            "password": "TestPass@123",
            "category": "General",
            "domicile": "Maharashtra",
            "exam": "MHT CET",
            "examScore": "150",
            "careerOption": "Engineering",
            "preferredBranch": "Computer Science",
            "preferredLocation": "Pune",
            "budgetRange": "10",
            "collegeType": "Government",
            "hostelRequired": False
        }
        print(f"  Payload keys: {list(payload_a.keys())}")
        resp_a = client.post("/api/auth/register", json=payload_a)
        print(f"  Response status: {resp_a.status_code}")
        print(f"  Response body: {resp_a.json()}")
        
        if resp_a.status_code == 200:
            # TEST B: Try same email again
            print(f"\nTest B: Register with SAME EMAIL as Test A")
            test_b_phone = f"8{unique_tag[:9]}"
            if len(test_b_phone) < 10:
                test_b_phone = test_b_phone + "0" * (10 - len(test_b_phone))
            payload_b = {**payload_a, "phone": test_b_phone}
            resp_b = client.post("/api/auth/register", json=payload_b)
            print(f"  Response status: {resp_b.status_code}")
            print(f"  Response body: {resp_b.json()}")
            
            # TEST C: Try same phone again
            print(f"\nTest C: Register with SAME PHONE as Test A")
            test_c_email = f"api-test-diff-{unique_tag}@example.com"
            payload_c = {**payload_a, "email": test_c_email}
            resp_c = client.post("/api/auth/register", json=payload_c)
            print(f"  Response status: {resp_c.status_code}")
            print(f"  Response body: {resp_c.json()}")
            
            # TEST D: Login with Test A credentials
            print(f"\nTest D: Login with Test A credentials (correct password)")
            resp_d = client.post("/api/auth/login", json={"username": test_a_email, "password": "TestPass@123"})
            print(f"  Response status: {resp_d.status_code}")
            body_d = resp_d.json()
            # Don't print full user, just key fields
            if 'user' in body_d:
                body_d['user'] = {k: v for k, v in body_d['user'].items() if k in ['id', 'uid', 'name', 'email', 'phone', 'role']}
            print(f"  Response body: {body_d}")
            
            # TEST E: Login with wrong password
            print(f"\nTest E: Login with Test A email (WRONG password)")
            resp_e = client.post("/api/auth/login", json={"username": test_a_email, "password": "WrongPass@123"})
            print(f"  Response status: {resp_e.status_code}")
            print(f"  Response body: {resp_e.json()}")
            
            # Clean up test users/profiles we created
            await db["users"].delete_many({"email": {"$regex": f"api-test-{unique_tag}"}})
            await db["profiles"].delete_many({"email": {"$regex": f"api-test-{unique_tag}"}})
            print(f"\nCleaned up test records.")
            
        else:
            print(f"  Initial register failed, skipping dependent tests.")
            
    except Exception as e:
        import traceback
        print(f"Error during API tests: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_indexes_and_test())
