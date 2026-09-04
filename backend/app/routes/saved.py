from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.saved import SavedCollegeCreate, SavedCollegeResponse
from app.routes.admin import track_analytics_event

router = APIRouter(prefix="/api/saved", tags=["Saved"])

@router.get("", response_model=List[SavedCollegeResponse])
async def get_saved_colleges(current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    collection = db["saved_colleges"]
    cursor = collection.find({"uid": current_user["uid"]}).sort("savedOn", -1)
    saved_list = await cursor.to_list(length=100)
    
    unique_colleges = []
    seen = set()
    for item in saved_list:
        item["id"] = str(item["_id"])
        del item["_id"]
        # Data migration on read for legacy documents
        if "collegeId" in item and "college_id" not in item:
            item["college_id"] = item.pop("collegeId")
            
        # Deduplicate based on college_id
        cid = item.get("college_id")
        if cid not in seen:
            seen.add(cid)
            unique_colleges.append(item)
        
    return unique_colleges

@router.post("", response_model=SavedCollegeResponse)
async def save_college(college: SavedCollegeCreate, current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    collection = db["saved_colleges"]
    
    cid = college.college_id or getattr(college, "collegeId", None) or college.name.lower().replace(" ", "-")
    
    # Check if already saved
    existing = await collection.find_one({
        "uid": current_user["uid"],
        "college_id": cid
    })
    
    if existing:
        existing["id"] = str(existing["_id"])
        del existing["_id"]
        return existing
        
    new_saved = college.model_dump()
    new_saved["college_id"] = cid
    new_saved["uid"] = current_user["uid"]
    new_saved["savedOn"] = datetime.now(timezone.utc)
    
    result = await collection.insert_one(new_saved)
    new_saved["id"] = str(result.inserted_id)
    del new_saved["_id"]
    await track_analytics_event(db, "COLLEGE_SAVED", user_id=current_user.get("uid"), college_id=cid, metadata={"savedId": new_saved["id"]})
    
    return new_saved

@router.delete("/{saved_id}")
async def remove_saved_college(saved_id: str, current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    collection = db["saved_colleges"]
    try:
        obj_id = ObjectId(saved_id)
    except Exception:
        # If the frontend passes college_id instead of saved document id
        delete_result = await collection.delete_one({"college_id": saved_id, "uid": current_user["uid"]})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Saved college not found")
        return {"status": "success", "message": "College removed from saved list"}

    delete_result = await collection.delete_one({"_id": obj_id, "uid": current_user["uid"]})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved college not found")
    await track_analytics_event(db, "COLLEGE_UNSAVED", user_id=current_user.get("uid"), college_id=saved_id, metadata={"source": "saved_route"})
    
    return {"status": "success", "message": "College removed from saved list"}
