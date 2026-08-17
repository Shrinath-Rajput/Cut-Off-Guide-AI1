from app.schemas.cutoff import CutoffSearchRequest, CutoffResult
from app.core.database import get_db

async def search_cutoffs(db, search_request: CutoffSearchRequest) -> CutoffResult:
    collection = db["cutoffs"]
    
    query = {}
    if search_request.course:
        query["course"] = {"$regex": search_request.course, "$options": "i"}
    if search_request.category:
        query["category"] = search_request.category
    if search_request.gender:
        query["gender"] = search_request.gender
    if search_request.university:
        query["university"] = {"$regex": search_request.university, "$options": "i"}
    if search_request.location:
        query["location"] = {"$regex": search_request.location, "$options": "i"}
    if search_request.round:
        query["round"] = search_request.round
    
    # Ideally, we should also filter by percentile.
    # We can fetch the highest cutoff that fits the user's percentile if it was provided,
    # or just the highest one matching the criteria.
    cutoff_record = await collection.find_one(query, sort=[("percentile", -1)])
    
    if cutoff_record:
        return CutoffResult(
            cutoff=str(cutoff_record.get("percentile", "N/A")),
            rank=str(cutoff_record.get("rank", "N/A")),
            suggestion=cutoff_record.get("college_name", "N/A")
        )
        
    return CutoffResult(
        cutoff="N/A",
        rank="N/A",
        suggestion="No exact matches found. Try adjusting your filters."
    )
