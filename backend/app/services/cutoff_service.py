from app.schemas.cutoff import CutoffSearchRequest, CutoffResult

async def search_cutoffs(db, search_request: CutoffSearchRequest) -> CutoffResult:
    if db is not None:
        try:
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
            
            cutoff_record = await collection.find_one(query, sort=[("percentile", -1)])
            if cutoff_record:
                return CutoffResult(
                    cutoff=str(cutoff_record.get("percentile", "94.5%ile")),
                    rank=str(cutoff_record.get("rank", "12,450")),
                    suggestion=cutoff_record.get("college_name", "COEP Tech / PICT Pune")
                )
        except Exception as e:
            print("Cutoffs DB lookup exception:", e)
        
    # Smart Fallback Estimation
    percentile = search_request.percentile or 90.0
    rank_est = int(max(1, (100 - percentile) * 1200))
    
    if percentile >= 98:
        sugg = "IIT Bombay / COEP Technological University (Computer Engg)"
    elif percentile >= 95:
        sugg = "VJTI Mumbai / PICT Pune / SPIT Mumbai (Information Tech)"
    elif percentile >= 90:
        sugg = "PCCOE Pune / VIT Pune / DYPCOE Akurdi (AI & Data Science)"
    elif percentile >= 80:
        sugg = "MIT-WPU Pune / Cummins College of Engg / DYPIT Pimpri"
    else:
        sugg = "State Autonomous & University Affiliated Colleges"

    return CutoffResult(
        cutoff=f"{percentile:.2f}%ile",
        rank=f"AIR ~{rank_est:,}",
        suggestion=sugg
    )
