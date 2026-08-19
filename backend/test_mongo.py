import asyncio
import os
from pprint import pprint
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongo_operations():
    print(f"Connecting to MongoDB at {settings.MONGODB_URI}")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    
    test_user = {
        "uid": "test_uid_123",
        "name": "Test User",
        "email": "test@example.com",
        "role": "USER"
    }

    print("\n--- 1. INSERT DATA ---")
    users_coll = db["users"]
    # Cleanup previous test data if any
    await users_coll.delete_many({"uid": "test_uid_123"})
    
    insert_result = await users_coll.insert_one(test_user)
    print(f"Inserted User with ID: {insert_result.inserted_id}")

    print("\n--- 2. READ DATA ---")
    read_user = await users_coll.find_one({"uid": "test_uid_123"})
    print("Read User:")
    pprint(read_user)
    assert read_user["name"] == "Test User"

    print("\n--- 3. UPDATE DATA ---")
    update_result = await users_coll.update_one(
        {"uid": "test_uid_123"},
        {"$set": {"name": "Test User Updated"}}
    )
    print(f"Matched: {update_result.matched_count}, Modified: {update_result.modified_count}")
    updated_user = await users_coll.find_one({"uid": "test_uid_123"})
    print("Updated User:")
    pprint(updated_user)
    assert updated_user["name"] == "Test User Updated"

    print("\n--- 4. DELETE DATA ---")
    delete_result = await users_coll.delete_one({"uid": "test_uid_123"})
    print(f"Deleted Count: {delete_result.deleted_count}")
    deleted_user = await users_coll.find_one({"uid": "test_uid_123"})
    print(f"Deleted User Exists: {deleted_user is not None}")
    assert deleted_user is None
    
    # Collections to ensure existence
    collections = await db.list_collection_names()
    print("\n--- 5. VERIFY COLLECTIONS ---")
    expected_collections = ["users", "colleges", "cutoffs", "profiles"]
    for coll in expected_collections:
        if coll not in collections:
            print(f"Creating collection {coll}")
            await db.create_collection(coll)
    
    collections = await db.list_collection_names()
    print(f"Collections present in db '{settings.MONGODB_DATABASE}':")
    print(collections)
    
    client.close()
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_mongo_operations())
