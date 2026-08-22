from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.core.deps import get_current_user_optional
from app.core.database import get_db
from app.schemas.profile import ProfileUpdate, ProfileResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/api/profile", tags=["Profile"])

_in_memory_profiles = {}


def _get_uid_for_request(current_user: Optional[dict], data: Optional[ProfileUpdate] = None) -> str:
    if current_user and (current_user.get("uid") or current_user.get("id")):
        return str(current_user.get("uid") or current_user.get("id"))
    if data and data.phone:
        return f"phone-{data.phone}"
    if data and data.email:
        return f"email-{data.email}"
    return "guest-user"


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db=Depends(get_db)
):
    uid = _get_uid_for_request(current_user)

    if db is not None:
        try:
            collection = db["profiles"]
            profile = await collection.find_one({"uid": uid})

            if not profile:
                new_profile = {
                    "uid": uid,
                    "name": current_user.get("name") if current_user else "User",
                    "email": current_user.get("email") if current_user else "",
                    "phone": current_user.get("phone") if current_user else "",
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc),
                }
                result = await collection.insert_one(new_profile)
                new_profile["id"] = str(result.inserted_id)
                if "_id" in new_profile:
                    del new_profile["_id"]
                return new_profile

            profile["id"] = str(profile.get("_id") or uid)
            if "_id" in profile:
                del profile["_id"]
            return profile
        except Exception as e:
            print("MongoDB get_profile error, fallback:", e)

    if uid not in _in_memory_profiles:
        _in_memory_profiles[uid] = {
            "id": f"prof-{uid}",
            "uid": uid,
            "name": current_user.get("name") if current_user else "User",
            "email": current_user.get("email") if current_user else "",
            "phone": current_user.get("phone") if current_user else "",
        }
    return _in_memory_profiles[uid]


@router.put("", response_model=ProfileResponse)
@router.post("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db=Depends(get_db),
):
    uid = _get_uid_for_request(current_user, profile_data)
    update_dict = profile_data.model_dump(exclude_unset=True)
    update_dict["updatedAt"] = datetime.now(timezone.utc)

    if db is not None:
        try:
            collection = db["profiles"]
            existing_profile = await collection.find_one({"uid": uid})

            if existing_profile:
                await collection.update_one({"uid": uid}, {"$set": update_dict})
            else:
                update_dict["uid"] = uid
                update_dict["createdAt"] = datetime.now(timezone.utc)
                await collection.insert_one(update_dict)

            updated_profile = await collection.find_one({"uid": uid})
            if updated_profile:
                updated_profile["id"] = str(updated_profile.get("_id") or uid)
                if "_id" in updated_profile:
                    del updated_profile["_id"]
                return updated_profile
        except Exception as e:
            print("MongoDB update_profile error, fallback:", e)

    if uid not in _in_memory_profiles:
        _in_memory_profiles[uid] = {"id": f"prof-{uid}", "uid": uid}
    _in_memory_profiles[uid].update(update_dict)
    _in_memory_profiles[uid]["id"] = str(_in_memory_profiles[uid].get("id", f"prof-{uid}"))
    _in_memory_profiles[uid]["uid"] = uid
    return _in_memory_profiles[uid]
