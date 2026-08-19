from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user
from app.core.database import get_db
from app.schemas.profile import ProfileUpdate, ProfileResponse
from datetime import datetime, timezone
from bson import ObjectId

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    collection = db["profiles"]
    profile = await collection.find_one({"uid": current_user["uid"]})
    
    if not profile:
        # Create an empty profile if not found
        new_profile = {
            "uid": current_user["uid"],
            "name": current_user.get("name"),
            "email": current_user.get("email"),
            "phone": current_user.get("phone"),
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        result = await collection.insert_one(new_profile)
        new_profile["id"] = str(result.inserted_id)
        if "_id" in new_profile:
            del new_profile["_id"]
        return new_profile

    profile["id"] = str(profile["_id"])
    del profile["_id"]
    return profile

@router.put("", response_model=ProfileResponse)
async def update_profile(profile_data: ProfileUpdate, current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    collection = db["profiles"]
    
    update_dict = profile_data.model_dump(exclude_unset=True)
    update_dict["updatedAt"] = datetime.now(timezone.utc)
    
    existing_profile = await collection.find_one({"uid": current_user["uid"]})
    
    if existing_profile:
        await collection.update_one(
            {"uid": current_user["uid"]},
            {"$set": update_dict}
        )
    else:
        update_dict["uid"] = current_user["uid"]
        update_dict["createdAt"] = datetime.now(timezone.utc)
        await collection.insert_one(update_dict)
        
    updated_profile = await collection.find_one({"uid": current_user["uid"]})
    updated_profile["id"] = str(updated_profile["_id"])
    del updated_profile["_id"]
    return updated_profile
