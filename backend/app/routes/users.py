from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "status": "success",
        "user": current_user
    }

@router.put("/me")
async def update_users_me(update_data: dict, current_user: dict = Depends(get_current_user)):
    # For now, just return the user, we can implement actual update logic later
    return {
        "status": "success",
        "message": "User profile updated",
        "user": current_user
    }
