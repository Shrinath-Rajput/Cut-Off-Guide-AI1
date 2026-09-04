from datetime import datetime, timedelta, timezone
import secrets
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
    for key, value in list(result.items()):
        if isinstance(value, (ObjectId, datetime)):
            result[key] = value.isoformat() if isinstance(value, datetime) else str(value)
        elif isinstance(value, dict):
            result[key] = _clean(value)
        elif isinstance(value, list):
            result[key] = [_clean(item) if isinstance(item, dict) else (item.isoformat() if isinstance(item, datetime) else str(item) if isinstance(item, ObjectId) else item) for item in value]
    return result


def _serialize_mongo_value(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _serialize_mongo_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize_mongo_value(item) for item in value]
    return value


def _query(search: Optional[str], fields: list[str]) -> dict:
    if not search:
        return {}
    return {"$or": [{field: {"$regex": search, "$options": "i"}} for field in fields]}


async def ensure_admin_account(db):
    configured_email = (settings.ADMIN_EMAIL or "").strip().lower()
    configured_password = settings.ADMIN_PASSWORD or ""
    if not configured_email or not configured_password:
        return

    user = await db["users"].find_one({"email": configured_email})
    if user:
        return

    now = datetime.now(timezone.utc)
    await db["users"].insert_one({
        "uid": f"admin-{uuid4().hex}", "name": "Administrator", "email": configured_email,
        "role": "ADMIN", "isActive": True, "passwordHash": get_password_hash(configured_password),
        "createdAt": now, "lastLogin": now,
    })


async def ensure_super_admin_account(db):
    configured_email = (settings.SUPER_ADMIN_EMAIL or "").strip().lower()
    configured_phone = (settings.SUPER_ADMIN_PHONE or "").strip()
    configured_password = settings.SUPER_ADMIN_PASSWORD or ""
    if not configured_email or not configured_password:
        return None

    existing = await db["users"].find_one({"role": "SUPER_ADMIN"})
    if existing:
        update = {
            "$set": {
                "email": configured_email,
                "phone": configured_phone,
                "role": "SUPER_ADMIN",
                "name": existing.get("name") or "FOURISE Super Admin",
                "isActive": True,
                "passwordHash": get_password_hash(configured_password),
                "lastLogin": datetime.now(timezone.utc),
                "provider": existing.get("provider") or "password",
            }
        }
        await db["users"].update_one({"_id": existing["_id"]}, update)
        return existing

    by_email = await db["users"].find_one({"email": configured_email})
    if by_email:
        await db["users"].update_one(
            {"_id": by_email["_id"]},
            {"$set": {"role": "SUPER_ADMIN", "phone": configured_phone, "isActive": True, "passwordHash": get_password_hash(configured_password), "lastLogin": datetime.now(timezone.utc), "provider": by_email.get("provider") or "password"}}
        )
        return by_email

    now = datetime.now(timezone.utc)
    created = {
        "uid": "super-admin-fourise",
        "name": "FOURISE Super Admin",
        "email": configured_email,
        "phone": configured_phone,
        "role": "SUPER_ADMIN",
        "isActive": True,
        "passwordHash": get_password_hash(configured_password),
        "createdAt": now,
        "lastLogin": now,
        "provider": "password",
    }
    await db["users"].insert_one(created)
    return created


def _safe_decode_token(token: str):
    from jose import jwt
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


@router.post("/login")
async def admin_login(request: AdminLoginRequest, db=Depends(get_db)):
    input_email = (request.email or "").strip().lower()
    input_password = request.password or ""
    configured_email = (settings.ADMIN_EMAIL or "").strip().lower()
    configured_password = settings.ADMIN_PASSWORD or ""
    super_email = (settings.SUPER_ADMIN_EMAIL or "").strip().lower()
    super_phone = (settings.SUPER_ADMIN_PHONE or "").strip()
    super_password = settings.SUPER_ADMIN_PASSWORD or ""

    if not input_email or not input_password:
        raise HTTPException(status_code=422, detail="Email and password are required")

    user = None
    role = None

    db_user = await db["users"].find_one({"email": input_email})
    if db_user and db_user.get("role") in {"ADMIN", "SUPER_ADMIN"}:
        user = db_user
        role = user.get("role") or "ADMIN"
        stored_hash = user.get("passwordHash") or user.get("password_hash")
        if not stored_hash or not verify_password(input_password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid admin credentials")

    if user is None and input_email == configured_email and configured_password:
        user = await db["users"].find_one({"email": configured_email})
        if user and user.get("role") not in {"ADMIN", "SUPER_ADMIN"}:
            user = None
        if user:
            role = user.get("role") or "ADMIN"
            stored_hash = user.get("passwordHash") or user.get("password_hash")
            if not stored_hash or not verify_password(input_password, stored_hash):
                raise HTTPException(status_code=401, detail="Invalid admin credentials")

    if user is None and super_email and (input_email == super_email or input_email == super_phone or request.email == super_phone):
        user = await db["users"].find_one({"$or": [{"email": super_email}, {"phone": super_phone}, {"role": "SUPER_ADMIN"}]})
        if user:
            role = user.get("role") or "SUPER_ADMIN"
            stored_hash = user.get("passwordHash") or user.get("password_hash")
            if not stored_hash or not verify_password(input_password, stored_hash):
                raise HTTPException(status_code=401, detail="Invalid admin credentials")

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    if role not in {"ADMIN", "SUPER_ADMIN"}:
        if input_email == configured_email:
            role = "ADMIN"
        elif input_email == super_email or input_email == super_phone:
            role = "SUPER_ADMIN"
        else:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")

    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"lastLogin": datetime.now(timezone.utc), "role": role, "isActive": True}})
    user = await db["users"].find_one({"_id": user["_id"]})
    user = _clean(user)
    user.pop("passwordHash", None)
    user.pop("password_hash", None)
    return {"status": "success", "token": create_access_token(user["uid"], role=role), "user": user}

async def track_analytics_event(db, event_type: str, user_id: Optional[str] = None, college_id: Optional[str] = None, metadata: Optional[dict] = None):
    if db is None:
        return None
    event = {"eventType": event_type, "timestamp": datetime.now(timezone.utc)}
    if user_id:
        event["userId"] = str(user_id)
    if college_id:
        event["collegeId"] = str(college_id)
    if metadata:
        event["metadata"] = metadata
    try:
        await db["analytics_events"].insert_one(event)
    except Exception:
        return None
    return event


async def _safe_count(collection, query: Optional[dict] = None) -> int:
    if collection is None:
        return 0
    try:
        return await collection.count_documents(query or {})
    except Exception:
        return 0


async def _safe_find_recent(collection, query: Optional[dict] = None, limit: int = 10):
    if collection is None:
        return []
    try:
        cursor = collection.find(query or {})
        if hasattr(cursor, "sort"):
            cursor = cursor.sort("timestamp", -1)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=limit)
    except Exception:
        return []


async def _safe_aggregate(collection, pipeline: list, limit: int = 5):
    if collection is None:
        return []
    try:
        cursor = collection.aggregate(pipeline)
        if hasattr(cursor, "to_list"):
            return await cursor.to_list(length=limit)
    except Exception:
        return []
    return []


async def get_super_admin_dashboard_secure(current_user: dict = Depends(require_admin), db = Depends(get_db)):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super admin access required")

    users = []
    try:
        users = await db["users"].find({}).to_list(length=5000)
    except Exception:
        users = []

    admin_count = sum(1 for user in users if user.get("role") == "ADMIN")
    super_admin_count = sum(1 for user in users if user.get("role") == "SUPER_ADMIN")
    total_users = len(users)
    total_colleges = await _safe_count(db["colleges"])
    total_searches = await _safe_count(db["analytics_events"], {"eventType": "COLLEGE_SEARCH"})
    total_visits = await _safe_count(db["analytics_events"], {"eventType": "COLLEGE_VIEW"})
    recent_searches = await _safe_find_recent(db["analytics_events"], {"eventType": "COLLEGE_SEARCH"}, 10)
    recent_visits = await _safe_find_recent(db["analytics_events"], {"eventType": "COLLEGE_VIEW"}, 10)
    recent_activity = await _safe_find_recent(db["analytics_events"], {}, 12)
    most_searched = await _safe_aggregate(db["analytics_events"], [
        {"$match": {"eventType": "COLLEGE_SEARCH"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ], 5)
    most_visited = await _safe_aggregate(db["analytics_events"], [
        {"$match": {"eventType": "COLLEGE_VIEW"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ], 5)

    recent_users = sorted(
        users,
        key=lambda item: item.get("createdAt") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )[:5]

    payload = {
        "status": "success",
        "data": {
            "summary": {
                "totalUsers": total_users,
                "totalColleges": total_colleges,
                "totalCollegeSearches": total_searches,
                "totalCollegeVisits": total_visits,
                "adminUsers": admin_count,
                "superAdminUsers": super_admin_count,
                "recentUsers": len([user for user in users if user.get("lastLogin")]),
                "activeUsers": len([user for user in users if user.get("isActive") is not False]),
            },
            "mostSearchedColleges": _serialize_mongo_value(most_searched),
            "mostVisitedColleges": _serialize_mongo_value(most_visited),
            "recentActivity": _serialize_mongo_value(recent_activity),
            "recentSearches": _serialize_mongo_value(recent_searches),
            "recentCollegeVisits": _serialize_mongo_value(recent_visits),
            "recentUsers": [_serialize_mongo_value(_clean(user)) for user in recent_users],
        }
    }
    return payload


@router.get("/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(require_admin), db = Depends(get_db)):
    users_count = await db["users"].count_documents({})
    enquiries_count = await db["enquiries"].count_documents({}) if "enquiries" in await db.list_collection_names() else 0
    colleges_count = await db["colleges"].count_documents({})
    cutoff_count = await db["cutoffs"].count_documents({})
    plans_count = await db["subscriptions"].count_documents({"isActive": True})
    total_searches = await db["analytics_events"].count_documents({"eventType": "COLLEGE_SEARCH"})
    total_visits = await db["analytics_events"].count_documents({"eventType": "COLLEGE_VIEW"})
    return {
        "status": "success",
        "data": {
            "totalUsers": users_count,
            "activeUsers": await db["users"].count_documents({"isActive": {"$ne": False}}),
            "totalEnquiries": enquiries_count,
            "totalColleges": colleges_count,
            "totalCutoffs": cutoff_count,
            "activePlans": plans_count,
            "totalCollegeSearches": total_searches,
            "totalCollegeVisits": total_visits,
            "recentUsers": [_clean(item) async for item in db["users"].find({}, {"passwordHash": 0, "password_hash": 0}).sort("createdAt", -1).limit(5)],
            "recentEnquiries": [_clean(item) async for item in db["enquiries"].find({}).sort("createdAt", -1).limit(5)] if "enquiries" in await db.list_collection_names() else [],
            "recentActivity": [_clean(item) async for item in db["analytics_events"].find({}).sort("timestamp", -1).limit(5)],
        }
    }


@router.get("/analytics")
async def get_admin_analytics(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    events = await db["analytics_events"].find({}).sort("timestamp", -1).limit(50).to_list(length=50)
    return {"status": "success", "data": events}


@router.get("/analytics/searches")
async def get_admin_analytics_searches(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    pipeline = [
        {"$match": {"eventType": "COLLEGE_SEARCH"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    data = await db["analytics_events"].aggregate(pipeline).to_list(length=10)
    return {"status": "success", "data": data}


@router.get("/analytics/college-visits")
async def get_admin_analytics_college_visits(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    pipeline = [
        {"$match": {"eventType": "COLLEGE_VIEW"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}, "uniqueVisitors": {"$addToSet": "$userId"}}},
        {"$project": {"_id": 0, "collegeId": "$_id", "count": 1, "uniqueVisitors": {"$size": "$uniqueVisitors"}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    data = await db["analytics_events"].aggregate(pipeline).to_list(length=10)
    return {"status": "success", "data": data}


@router.get("/analytics/website-visits")
async def get_admin_analytics_website_visits(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    pipeline = [
        {"$match": {"eventType": "PAGE_VIEW"}},
        {"$group": {"_id": "$metadata.page", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    data = await db["analytics_events"].aggregate(pipeline).to_list(length=10)
    return {"status": "success", "data": data}


@router.get("/analytics/predictions")
async def get_admin_analytics_predictions(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    data = await db["analytics_events"].find({"eventType": "PREDICTION_GENERATED"}).sort("timestamp", -1).limit(20).to_list(length=20)
    return {"status": "success", "data": data}


@router.get("/analytics/comparisons")
async def get_admin_analytics_comparisons(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    data = await db["analytics_events"].find({"eventType": "COLLEGE_COMPARE"}).sort("timestamp", -1).limit(20).to_list(length=20)
    return {"status": "success", "data": data}


@router.get("/analytics/subscriptions")
async def get_admin_analytics_subscriptions(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    data = await db["subscriptions"].find({}).to_list(length=100)
    return {"status": "success", "data": data}


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

class BulkCutoffImportRequest(BaseModel):
    year: int
    data_type: str = "actual"
    records: list[dict[str, Any]]

@router.post("/cutoffs/bulk-import")
async def bulk_import_cutoffs(payload: BulkCutoffImportRequest, current_user: dict = Depends(require_admin), db=Depends(get_db)):
    """Import a batch of cutoff data marked as ACTUAL for a specific year, triggering immediate availability for 2027 prediction recalculations."""
    now = datetime.now(timezone.utc)
    documents = []
    for r in payload.records:
        r["year"] = payload.year
        r["data_type"] = payload.data_type
        r["createdAt"] = now
        documents.append(r)
        
    if not documents:
        raise HTTPException(status_code=400, detail="No records provided")
        
    result = await db["cutoffs"].insert_many(documents)
    return {
        "status": "success", 
        "inserted_count": len(result.inserted_ids),
        "year": payload.year,
        "data_type": payload.data_type,
        "message": f"Successfully imported {len(result.inserted_ids)} records as {payload.data_type} data for {payload.year}."
    }


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
