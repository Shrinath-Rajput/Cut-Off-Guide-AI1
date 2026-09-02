from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.schemas.cutoff import CutoffSearchRequest, CutoffResult
from app.services.cutoff_service import search_cutoffs

router = APIRouter(prefix="/api/cutoffs", tags=["Cutoffs"])


@router.post("/search", response_model=CutoffResult)
async def search_cutoffs_endpoint(request: CutoffSearchRequest, db = Depends(get_db)):
    required_fields = [
        "exam",
        "score",
        "category",
        "gender",
        "university",
        "course",
        "location",
        "round",
    ]
    missing = [field for field in required_fields if not getattr(request, field, None)]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required cutoff fields: {', '.join(missing)}",
        )

    try:
        result = await search_cutoffs(db, request)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
