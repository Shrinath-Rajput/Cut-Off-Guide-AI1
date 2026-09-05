import asyncio
from app.core.database import connect_to_mongo, get_db, close_mongo_connection
from app.schemas.prediction import PredictionRequest
from app.services.prediction_service import get_cutoff_prediction

async def test_prediction():
    await connect_to_mongo()
    db = get_db()
    
    # Test 1: Historical data through 2025. 2026 unavailable. Target 2027.
    req = PredictionRequest(
        college="VJTI",
        course="Computer",
        target_year=2027
    )
    
    res = await get_cutoff_prediction(db, req)
    print("TEST 1 - Prediction for VJTI Computer 2027:")
    print(res.model_dump_json(indent=2) if hasattr(res, 'model_dump_json') else res)
    
    # Test 2: Add 2026 actual data manually to db, then re-predict
    await db.cutoffs.insert_one({
        "course": "Computer Engineering",
        "category": "Open",
        "gender": "Male",
        "college_name": "VJTI Mumbai",
        "percentile": "99.8",
        "year": 2026,
        "data_type": "actual"
    })
    
    res2 = await get_cutoff_prediction(db, req)
    print("\nTEST 2 - Prediction after adding 2026 data:")
    print(res2.model_dump_json(indent=2) if hasattr(res2, 'model_dump_json') else res2)
    
    # Cleanup 2026 data
    await db.cutoffs.delete_one({"year": 2026, "college_name": "VJTI Mumbai"})
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_prediction())
