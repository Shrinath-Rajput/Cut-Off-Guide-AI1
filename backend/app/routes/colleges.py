from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from app.core.database import get_db
from app.schemas.college import CollegeResponse, PaginatedCollegeResponse
from app.services.college_service import get_all_colleges, get_college_by_id
from app.routes.admin import track_analytics_event

router = APIRouter(prefix="/api/colleges", tags=["Colleges"])

@router.get("", response_model=PaginatedCollegeResponse)
async def list_colleges(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    state: Optional[str] = None,
    states: Optional[List[str]] = Query(None),
    courses: Optional[List[str]] = Query(None),
    max_fee: Optional[int] = None,
    college_type: Optional[str] = None,
    sort: Optional[str] = None,
    db = Depends(get_db)
):
    # Collect all states from query parameters
    selected_states = []
    if states:
        selected_states.extend(states)
    if state:
        selected_states.append(state)

    # Check raw query params for states[] or state
    for k, v in request.query_params.multi_items():
        if k.startswith("states") or k == "state":
            if v and v not in selected_states:
                selected_states.append(v)

    colleges = await get_all_colleges(
        db, 
        page=page, 
        limit=limit, 
        search=search, 
        states=selected_states if selected_states else None, 
        courses=courses, 
        max_fee=max_fee, 
        college_type=college_type, 
        sort=sort
    )
    if search:
        await track_analytics_event(db, "COLLEGE_SEARCH", metadata={"search": search, "page": page, "limit": limit})
    return colleges

@router.get("/ai/lookup")
async def lookup_college_ai(q: str = Query(..., min_length=1, description="College name or query")):
    from app.services.college_service import generate_college_ai_info
    info = generate_college_ai_info(q.strip())
    return {"status": "success", "data": info}

@router.get("/compare/ai")
async def compare_colleges_ai_endpoint(
    c1: Optional[str] = None,
    c2: Optional[str] = None,
    college1: Optional[str] = None,
    college2: Optional[str] = None,
):
    first = college1 or c1
    second = college2 or c2
    if not first or not second:
        raise HTTPException(status_code=400, detail="Both college1 (c1) and college2 (c2) parameters are required for comparison.")
    
    from app.services.college_service import compare_two_colleges_ai
    comparison = compare_two_colleges_ai(first.strip(), second.strip())
    return {"status": "success", "data": comparison}

@router.get("/{college_id}", response_model=CollegeResponse)
async def read_college(college_id: str, db = Depends(get_db)):
    college = await get_college_by_id(db, college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    await track_analytics_event(db, "COLLEGE_VIEW", college_id=college_id, metadata={"college_name": college.get("name")})
    return college
