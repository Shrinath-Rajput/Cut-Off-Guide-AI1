from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.core.deps import require_admin
from app.core.database import get_db
from app.services.image_storage import save_college_image

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


@router.get("/colleges")
async def get_admin_colleges(current_user: dict = Depends(require_admin), db=Depends(get_db)):
    colleges = await db["colleges"].find({}, {"_id": 0}).sort("rank", 1).to_list(length=None)
    for college in colleges:
        college.setdefault("image", None)
    return {"data": colleges}


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
