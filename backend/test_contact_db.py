import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def test_insert():
    try:
        print("Connecting to MongoDB...")
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        db = client["CutOffGrid"]  # need to know db name!
        
        # Or let's import settings and test via their code
        from app.core.database import connect_to_mongo, get_db
        await connect_to_mongo()
        db = get_db()
        print(f"DB instance: {db}")
        
        inquiry_doc = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "General Inquiry",
            "message": "This is a test message. Please assist.",
            "createdAt": datetime.utcnow(),
            "status": "unread"
        }
        
        print("Inserting document...")
        result = await db["enquiries"].insert_one(inquiry_doc)
        print(f"Inserted document with ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_insert())
