from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


async def ensure_super_admin_account(db):
    configured_email = (settings.SUPER_ADMIN_EMAIL or "").strip().lower()
    configured_phone = (settings.SUPER_ADMIN_PHONE or "").strip()
    configured_password = settings.SUPER_ADMIN_PASSWORD or ""

    if db is None or not configured_email or not configured_password:
        return None

    existing = await db["users"].find_one({"$or": [{"email": configured_email}, {"phone": configured_phone}, {"role": "SUPER_ADMIN"}]})
    if existing:
        update = {"$set": {"email": configured_email, "phone": configured_phone, "role": "SUPER_ADMIN", "isActive": True, "passwordHash": get_password_hash(configured_password), "lastLogin": datetime.now(timezone.utc)}}
        await db["users"].update_one({"_id": existing["_id"]}, update)
        return existing

    document = {
        "uid": "super-admin-fourise",
        "name": "FOURISE Super Admin",
        "email": configured_email,
        "phone": configured_phone,
        "role": "SUPER_ADMIN",
        "isActive": True,
        "passwordHash": get_password_hash(configured_password),
        "createdAt": datetime.now(timezone.utc),
        "lastLogin": datetime.now(timezone.utc),
        "provider": "password",
    }
    await db["users"].insert_one(document)
    return document


async def require_super_admin(current_user: dict = Depends(get_current_user)):
    role = (current_user or {}).get("role")
    if role != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    return current_user


@router.post("/super-admin/login")
async def super_admin_login(payload: Dict[str, Any], db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    email = str(payload.get("email") or "").strip().lower()
    phone = str(payload.get("phone") or "").strip()
    password = str(payload.get("password") or "")

    if not email and not phone:
        raise HTTPException(status_code=400, detail="Email or phone is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    query = {"$or": [{"email": email}, {"phone": phone}, {"role": "SUPER_ADMIN"}]}
    user = await db["users"].find_one(query)
    if not user or user.get("role") != "SUPER_ADMIN":
        raise HTTPException(status_code=401, detail="Unauthorized super admin account")

    stored_hash = user.get("passwordHash") or user.get("password_hash")
    if not stored_hash or not verify_password(password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid super admin credentials")

    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"lastLogin": datetime.now(timezone.utc)}})
    user_data = dict(user)
    user_data["id"] = str(user_data.pop("_id"))
    user_data.pop("passwordHash", None)
    user_data.pop("password_hash", None)
    token = create_access_token(user_data["uid"], role="SUPER_ADMIN")
    return {"status": "success", "token": token, "user": user_data}


@router.get("/super-admin/dashboard")
async def get_super_admin_dashboard(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    now = datetime.now(timezone.utc)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = now - timedelta(days=6)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    try:
        users = await db["users"].find({}).to_list(length=5000)
    except Exception:
        users = []

    admin_count = sum(1 for user in users if user.get("role") == "ADMIN")
    super_admin_count = sum(1 for user in users if user.get("role") == "SUPER_ADMIN")
    total_colleges = await db["colleges"].count_documents({})
    total_users = len(users)

    total_searches = await db["analytics_events"].count_documents({"eventType": "COLLEGE_SEARCH"})
    total_visits = await db["analytics_events"].count_documents({"eventType": "COLLEGE_VIEW"})

    recent_searches = await db["analytics_events"].find({"eventType": "COLLEGE_SEARCH"}).sort("timestamp", -1).limit(10).to_list(length=10)
    recent_visits = await db["analytics_events"].find({"eventType": "COLLEGE_VIEW"}).sort("timestamp", -1).limit(10).to_list(length=10)
    recent_activity = await db["analytics_events"].find({}).sort("timestamp", -1).limit(12).to_list(length=12)

    most_searched = await db["analytics_events"].aggregate([
        {"$match": {"eventType": "COLLEGE_SEARCH"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(length=5)
    most_visited = await db["analytics_events"].aggregate([
        {"$match": {"eventType": "COLLEGE_VIEW"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(length=5)

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
                "newRegistrationsToday": await db["users"].count_documents({"createdAt": {"$gte": start_of_today}}),
                "newRegistrationsThisWeek": await db["users"].count_documents({"createdAt": {"$gte": start_of_week}}),
                "newRegistrationsThisMonth": await db["users"].count_documents({"createdAt": {"$gte": start_of_month}}),
                "dailyActiveUsers": await db["analytics_events"].count_documents({"eventType": "USER_LOGIN", "timestamp": {"$gte": start_of_today}}),
                "weeklyActiveUsers": await db["analytics_events"].count_documents({"eventType": "USER_LOGIN", "timestamp": {"$gte": start_of_week}}),
                "monthlyActiveUsers": await db["analytics_events"].count_documents({"eventType": "USER_LOGIN", "timestamp": {"$gte": start_of_month}}),
                "searchesToday": await db["analytics_events"].count_documents({"eventType": "COLLEGE_SEARCH", "timestamp": {"$gte": start_of_today}}),
                "searchesThisWeek": await db["analytics_events"].count_documents({"eventType": "COLLEGE_SEARCH", "timestamp": {"$gte": start_of_week}}),
                "searchesThisMonth": await db["analytics_events"].count_documents({"eventType": "COLLEGE_SEARCH", "timestamp": {"$gte": start_of_month}}),
                "visitsToday": await db["analytics_events"].count_documents({"eventType": "COLLEGE_VIEW", "timestamp": {"$gte": start_of_today}}),
                "visitsThisWeek": await db["analytics_events"].count_documents({"eventType": "COLLEGE_VIEW", "timestamp": {"$gte": start_of_week}}),
                "visitsThisMonth": await db["analytics_events"].count_documents({"eventType": "COLLEGE_VIEW", "timestamp": {"$gte": start_of_month}}),
            },
            "mostSearchedColleges": [
                {**item, "_id": str(item.get("_id")) if item.get("_id") is not None else None}
                for item in most_searched
            ],
            "mostVisitedColleges": [
                {**item, "_id": str(item.get("_id")) if item.get("_id") is not None else None}
                for item in most_visited
            ],
            "recentSearches": [
                {**item, "_id": str(item.get("_id")) if item.get("_id") is not None else None}
                for item in recent_searches
            ],
            "recentCollegeVisits": [
                {**item, "_id": str(item.get("_id")) if item.get("_id") is not None else None}
                for item in recent_visits
            ],
            "recentActivity": [
                {**item, "_id": str(item.get("_id")) if item.get("_id") is not None else None}
                for item in recent_activity
            ],
            "recentUsers": [
                {
                    **user,
                    "id": str(user.get("_id")) if user.get("_id") is not None else user.get("id"),
                    "_id": str(user.get("_id")) if user.get("_id") is not None else user.get("_id"),
                }
                for user in recent_users
            ],
        },
    }
    return payload


@router.get("/analytics")
async def get_analytics(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    events = await db["analytics_events"].find({}).sort("timestamp", -1).limit(50).to_list(length=50)
    return {"status": "success", "data": events}


@router.get("/analytics/searches")
async def get_analytics_searches(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    searches = await db["analytics_events"].aggregate([
        {"$match": {"eventType": "COLLEGE_SEARCH"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]).to_list(length=10)
    return {"status": "success", "data": searches}


@router.get("/analytics/college-visits")
async def get_analytics_college_visits(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    visits = await db["analytics_events"].aggregate([
        {"$match": {"eventType": "COLLEGE_VIEW"}},
        {"$group": {"_id": "$collegeId", "count": {"$sum": 1}, "uniqueVisitors": {"$addToSet": "$userId"}}},
        {"$project": {"_id": 0, "collegeId": "$_id", "count": 1, "uniqueVisitors": {"$size": "$uniqueVisitors"}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]).to_list(length=10)
    return {"status": "success", "data": visits}


@router.get("/analytics/website-visits")
async def get_analytics_website_visits(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    visits = await db["analytics_events"].aggregate([
        {"$match": {"eventType": "PAGE_VIEW"}},
        {"$group": {"_id": "$metadata.page", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]).to_list(length=10)
    return {"status": "success", "data": visits}


@router.get("/analytics/predictions")
async def get_analytics_predictions(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    predictions = await db["analytics_events"].find({"eventType": "PREDICTION_GENERATED"}).sort("timestamp", -1).limit(50).to_list(length=50)
    return {"status": "success", "data": predictions}


@router.get("/analytics/comparisons")
async def get_analytics_comparisons(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    comparisons = await db["analytics_events"].find({"eventType": "COLLEGE_COMPARE"}).sort("timestamp", -1).limit(50).to_list(length=50)
    return {"status": "success", "data": comparisons}


@router.get("/analytics/subscriptions")
async def get_analytics_subscriptions(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    plans = await db["subscriptions"].find({}).to_list(length=100)
    return {"status": "success", "data": plans}


@router.get("/users")
async def list_super_admin_users(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_super_admin),
    db=Depends(get_db)
):
    query = {}
    if search:
        query = {"$or": [{"name": {"$regex": search, "$options": "i"}}, {"email": {"$regex": search, "$options": "i"}}, {"phone": {"$regex": search, "$options": "i"}}]}
    total = await db["users"].count_documents(query)
    items = await db["users"].find(query, {"passwordHash": 0, "password_hash": 0}).sort("createdAt", -1).skip((page - 1) * limit).limit(limit).to_list(length=limit)
    return {"data": items, "total": total, "page": page, "limit": limit, "totalPages": max(1, (total + limit - 1) // limit)}


@router.get("/users/{user_id}")
async def get_super_admin_user(user_id: str, current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    try:
        obj_id = ObjectId(user_id)
        user = await db["users"].find_one({"_id": obj_id}, {"passwordHash": 0, "password_hash": 0})
    except Exception:
        user = await db["users"].find_one({"uid": user_id}, {"passwordHash": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "data": user}


@router.put("/users/{user_id}/status")
async def update_user_status(user_id: str, payload: Dict[str, Any], current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    is_active = payload.get("isActive")
    if is_active is None:
        raise HTTPException(status_code=400, detail="isActive is required")
    try:
        result = await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"isActive": bool(is_active)}})
    except Exception:
        result = await db["users"].update_one({"uid": user_id}, {"$set": {"isActive": bool(is_active)}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success"}


@router.get("/colleges")
async def get_super_admin_colleges(current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    colleges = await db["colleges"].find({}).sort("rank", 1).to_list(length=1000)
    return {"status": "success", "data": colleges}


@router.post("/colleges")
async def create_super_admin_college(payload: Dict[str, Any], current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    payload.setdefault("id", f"college-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    payload.setdefault("createdAt", datetime.now(timezone.utc))
    await db["colleges"].insert_one(payload)
    return {"status": "success", "data": payload}


@router.get("/colleges/{college_id}")
async def get_super_admin_college(college_id: str, current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    college = await db["colleges"].find_one({"id": college_id})
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return {"status": "success", "data": college}


@router.put("/colleges/{college_id}")
async def update_super_admin_college(college_id: str, payload: Dict[str, Any], current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    payload.pop("_id", None)
    result = await db["colleges"].update_one({"id": college_id}, {"$set": payload})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="College not found")
    return {"status": "success"}


@router.delete("/colleges/{college_id}")
async def delete_super_admin_college(college_id: str, current_user: dict = Depends(require_super_admin), db=Depends(get_db)):
    result = await db["colleges"].delete_one({"id": college_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="College not found")
    return {"status": "success"}
