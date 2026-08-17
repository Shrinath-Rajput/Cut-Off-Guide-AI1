from typing import List, Dict, Any, Optional
from app.core.database import get_db

async def get_all_colleges(
    db, 
    page: int = 1, 
    limit: int = 10, 
    search: Optional[str] = None,
    states: Optional[List[str]] = None,
    courses: Optional[List[str]] = None,
    max_fee: Optional[int] = None,
    college_type: Optional[str] = None,
    sort: Optional[str] = None
) -> Dict[str, Any]:
    collection = db["colleges"]
    
    query = {}
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
        
    if states:
        query["state"] = {"$in": states}
        
    if courses:
        query["courses"] = {"$in": courses}
        
    if max_fee is not None:
        query["feeValue"] = {"$lte": max_fee}
        
    if college_type:
        query["type"] = college_type

    sort_options = [("rank", 1)]  # default sort
    if sort == "ranking":
        sort_options = [("rank", 1)]
    elif sort == "fees":
        sort_options = [("feeValue", 1)]

    skip = (page - 1) * limit
    
    total = await collection.count_documents(query)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    colleges_cursor = collection.find(query).sort(sort_options).skip(skip).limit(limit)
    colleges = await colleges_cursor.to_list(length=limit)
    
    for college in colleges:
        if "id" not in college:
            college["id"] = str(college["_id"])
            
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "data": colleges
    }
async def get_college_by_id(db, college_id: str) -> Optional[Dict[str, Any]]:
    collection = db["colleges"]
    college = await collection.find_one({"id": college_id})
    if college and "id" not in college:
        college["id"] = str(college["_id"])
    return college
