from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.schemas.cutoff import CutoffSearchRequest, CutoffResult
from app.services.cutoff_service import search_cutoffs

router = APIRouter(prefix="/api/cutoffs", tags=["Cutoffs"])

@router.post("/search", response_model=CutoffResult)
async def search_cutoffs_endpoint(request: CutoffSearchRequest, db = Depends(get_db)):
    result = await search_cutoffs(db, request)
    return result
