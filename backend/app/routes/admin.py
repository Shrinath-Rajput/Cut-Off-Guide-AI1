from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_admin
from app.core.database import get_db

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(require_admin), db = Depends(get_db)):
    users_count = await db["users"].count_documents({})
    colleges_count = await db["colleges"].count_documents({})
    return {
        "status": "success",
        "data": {
            "users": users_count,
            "colleges": colleges_count
        }
    }
