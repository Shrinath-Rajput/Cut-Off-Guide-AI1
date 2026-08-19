from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.core.database import get_db
from app.schemas.college import CollegeResponse, PaginatedCollegeResponse
from app.services.college_service import get_all_colleges, get_college_by_id

router = APIRouter(prefix="/api/colleges", tags=["Colleges"])

@router.get("", response_model=PaginatedCollegeResponse)
async def list_colleges(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    states: Optional[List[str]] = Query(None),
    courses: Optional[List[str]] = Query(None),
    max_fee: Optional[int] = None,
    college_type: Optional[str] = None,
    sort: Optional[str] = None,
    db = Depends(get_db)
):
    colleges = await get_all_colleges(
        db, 
        page=page, 
        limit=limit, 
        search=search, 
        states=states, 
        courses=courses, 
        max_fee=max_fee, 
        college_type=college_type, 
        sort=sort
    )
    return colleges

@router.get("/{college_id}", response_model=CollegeResponse)
async def read_college(college_id: str, db = Depends(get_db)):
    college = await get_college_by_id(db, college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college
