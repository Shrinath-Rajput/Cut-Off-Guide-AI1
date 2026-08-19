from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from app.core.deps import require_admin
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.services.image_storage import save_college_image, save_ui_image

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminRecord(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "USER"
    isActive: bool = True


class EnquiryUpdate(BaseModel):
    status: Optional[str] = None
    response: Optional[str] = None


class TrainRequest(BaseModel):
    source: str = "database"


def _clean(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return document
    result = dict(document)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    return result


def _query(search: Optional[str], fields: list[str]) -> dict:
    if not search:
        return {}
    return {"$or": [{field: {"$regex": search, "$options": "i"}} for field in fields]}


@router.post("/login")
async def admin_login(request: AdminLoginRequest, db=Depends(get_db)):
    user = await db["users"].find_one({"email": request.email, "role": "ADMIN"})
    if not user and settings.ADMIN_EMAIL and request.email.lower() == settings.ADMIN_EMAIL.lower():
        if not settings.ADMIN_PASSWORD or request.password != settings.ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        now = datetime.now(timezone.utc)
        result = await db["users"].insert_one({
            "uid": f"admin-{uuid4().hex}", "name": "Administrator", "email": request.email,
            "role": "ADMIN", "isActive": True, "passwordHash": get_password_hash(request.password),
            "createdAt": now, "lastLogin": now,
        })
        user = await db["users"].find_one({"_id": result.inserted_id})
    password_hash = user.get("passwordHash") if user else None
    password_hash = password_hash or (user or {}).get("password_hash")
    if not user or not user.get("isActive", True) or not password_hash or not verify_password(request.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"lastLogin": datetime.now(timezone.utc)}})
    user = _clean(user)
    user.pop("passwordHash", None)
    user.pop("password_hash", None)
    return {"status": "success", "token": create_access_token(user["uid"], role="ADMIN"), "user": user}

@router.get("/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(require_admin), db = Depends(get_db)):
    users_count = await db["users"].count_documents({})
    enquiries_count = await db["enquiries"].count_documents({})
    colleges_count = await db["colleges"].count_documents({})
    cutoff_count = await db["cutoffs"].count_documents({})
    plans_count = await db["subscriptions"].count_documents({"isActive": True})
    return {
        "status": "success",
        "data": {
            "totalUsers": users_count,
            "activeUsers": await db["users"].count_documents({"isActive": {"$ne": False}}),
            "totalEnquiries": enquiries_count,
            "totalColleges": colleges_count,
            "totalCutoffs": cutoff_count,
            "activePlans": plans_count,
            "recentUsers": [_clean(item) async for item in db["users"].find({}, {"passwordHash": 0, "password_hash": 0}).sort("createdAt", -1).limit(5)],
            "recentEnquiries": [_clean(item) async for item in db["enquiries"].find({}).sort("createdAt", -1).limit(5)],
            "recentActivity": [],
        }
    }


@router.get("/users")
async def list_users(search: Optional[str] = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), current_user: dict = Depends(require_admin), db=Depends(get_db)):
    query = _query(search, ["name", "email", "phone"])
    total = await db["users"].count_documents(query)
    cursor = db["users"].find(query, {"passwordHash": 0, "password_hash": 0}).sort("createdAt", -1).skip((page - 1) * limit).limit(limit)
    return {"data": [_clean(item) async for item in cursor], "total": total, "page": page, "limit": limit, "totalPages": max(1, (total + limit - 1) // limit)}


@router.patch("/users/{user_id}")
async def update_user(user_id: str, payload: AdminRecord, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": payload.model_dump(exclude={"role"})})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "data": _clean(await db["users"].find_one({"_id": ObjectId(user_id)}, {"passwordHash": 0, "password_hash": 0}))}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    if user_id == current_user.get("id"):
        raise HTTPException(status_code=400, detail="You cannot delete the current admin")
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success"}


@router.get("/colleges")
async def get_admin_colleges(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    colleges = await db["colleges"].find({}, {"_id": 0}).sort("rank", 1).to_list(length=None)
    for college in colleges:
        college.setdefault("image", None)
    return {"data": colleges}


@router.post("/colleges")
async def create_college(payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    payload.setdefault("id", uuid4().hex)
    payload.setdefault("createdAt", datetime.now(timezone.utc))
    await db["colleges"].insert_one(payload)
    return {"status": "success", "data": _clean(payload)}


@router.put("/colleges/{college_id}")
async def update_college(college_id: str, payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    payload.pop("_id", None)
    result = await db["colleges"].update_one({"id": college_id}, {"$set": payload})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="College not found")
    return {"status": "success", "data": _clean(await db["colleges"].find_one({"id": college_id}))}


@router.delete("/colleges/{college_id}")
async def delete_college(college_id: str, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["colleges"].delete_one({"id": college_id})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="College not found")
    return {"status": "success"}


@router.get("/cutoffs")
async def list_cutoffs(search: Optional[str] = None, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    return {"data": [_clean(item) async for item in db["cutoffs"].find(_query(search, ["college_name", "course", "category"])).sort("percentile", -1).limit(500)]}


@router.post("/cutoffs")
async def create_cutoff(payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    payload.setdefault("createdAt", datetime.now(timezone.utc))
    result = await db["cutoffs"].insert_one(payload)
    return {"status": "success", "data": _clean({**payload, "_id": result.inserted_id})}


@router.put("/cutoffs/{cutoff_id}")
async def update_cutoff(cutoff_id: str, payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["cutoffs"].update_one({"_id": ObjectId(cutoff_id)}, {"$set": payload})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Cutoff record not found")
    return {"status": "success", "data": _clean(await db["cutoffs"].find_one({"_id": ObjectId(cutoff_id)}))}


@router.delete("/cutoffs/{cutoff_id}")
async def delete_cutoff(cutoff_id: str, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["cutoffs"].delete_one({"_id": ObjectId(cutoff_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Cutoff record not found")
    return {"status": "success"}


@router.get("/enquiries")
async def list_enquiries(search: Optional[str] = None, enquiry_status: Optional[str] = None, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    query = _query(search, ["subject", "message", "email", "name"])
    if enquiry_status:
        query["status"] = enquiry_status
    return {"data": [_clean(item) async for item in db["enquiries"].find(query).sort("createdAt", -1).limit(500)]}


@router.patch("/enquiries/{enquiry_id}")
async def update_enquiry(enquiry_id: str, payload: EnquiryUpdate, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    update = {key: value for key, value in payload.model_dump().items() if value is not None}
    update["updatedAt"] = datetime.now(timezone.utc)
    result = await db["enquiries"].update_one({"_id": ObjectId(enquiry_id)}, {"$set": update})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return {"status": "success", "data": _clean(await db["enquiries"].find_one({"_id": ObjectId(enquiry_id)}))}


@router.delete("/enquiries/{enquiry_id}")
async def delete_enquiry(enquiry_id: str, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["enquiries"].delete_one({"_id": ObjectId(enquiry_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return {"status": "success"}


@router.get("/subscriptions")
async def list_subscriptions(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    return {"data": [_clean(item) async for item in db["subscriptions"].find({}).sort("price", 1)]}


@router.post("/subscriptions")
async def create_subscription(payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    payload.setdefault("isActive", True)
    payload.setdefault("createdAt", datetime.now(timezone.utc))
    result = await db["subscriptions"].insert_one(payload)
    return {"status": "success", "data": _clean({**payload, "_id": result.inserted_id})}


@router.put("/subscriptions/{plan_id}")
async def update_subscription(plan_id: str, payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["subscriptions"].update_one({"_id": ObjectId(plan_id)}, {"$set": payload})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return {"status": "success", "data": _clean(await db["subscriptions"].find_one({"_id": ObjectId(plan_id)}))}


@router.delete("/subscriptions/{plan_id}")
async def delete_subscription(plan_id: str, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["subscriptions"].delete_one({"_id": ObjectId(plan_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return {"status": "success"}


@router.post("/train")
async def train_database(source: str = "database", current_user: dict = Depends(require_admin), db=Depends(get_db)):
    return {"status": "not_configured", "message": "Database records are available. No model trainer is configured in this deployment.", "source": source}


@router.post("/colleges/{college_id}/image")
async def upload_college_image(
    college_id: str,
    image: UploadFile = File(...),
    current_user: dict = Depends(require_admin),
    db=Depends(get_db),
):
    college = await db["colleges"].find_one({"id": college_id})
    if not college:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")

    image_url = await save_college_image(image)
    await db["colleges"].update_one({"_id": college["_id"]}, {"$set": {"image": image_url}})
    return {"status": "success", "college_id": college_id, "image": image_url}


@router.get("/images")
async def list_images(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    return {"data": [_clean(item) async for item in db["ui_images"].find({}).sort("updatedAt", -1)]}


@router.post("/images")
async def upload_ui_image(
    image: UploadFile = File(...),
    section: str = "Home Hero",
    name: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db=Depends(get_db),
):
    image_url = await save_ui_image(image)
    now = datetime.now(timezone.utc)
    document = {"name": name or image.filename or "UI image", "section": section, "url": image_url, "isActive": True, "createdAt": now, "updatedAt": now}
    result = await db["ui_images"].insert_one(document)
    return {"status": "success", "data": _clean({**document, "_id": result.inserted_id})}


@router.patch("/images/{image_id}")
async def update_ui_image(image_id: str, payload: dict[str, Any], current_user: dict = Depends(require_admin), db=Depends(get_db)):
    payload["updatedAt"] = datetime.now(timezone.utc)
    result = await db["ui_images"].update_one({"_id": ObjectId(image_id)}, {"$set": payload})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"status": "success", "data": _clean(await db["ui_images"].find_one({"_id": ObjectId(image_id)}))}


@router.post("/images/{image_id}/replace")
async def replace_ui_image(image_id: str, image: UploadFile = File(...), current_user: dict = Depends(require_admin), db=Depends(get_db)):
    existing = await db["ui_images"].find_one({"_id": ObjectId(image_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Image not found")
    image_url = await save_ui_image(image)
    await db["ui_images"].update_one({"_id": ObjectId(image_id)}, {"$set": {"url": image_url, "updatedAt": datetime.now(timezone.utc), "name": image.filename or existing.get("name", "UI image")}})
    return {"status": "success", "data": _clean(await db["ui_images"].find_one({"_id": ObjectId(image_id)}))}


@router.delete("/images/{image_id}")
async def delete_ui_image(image_id: str, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    result = await db["ui_images"].delete_one({"_id": ObjectId(image_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"status": "success"}
