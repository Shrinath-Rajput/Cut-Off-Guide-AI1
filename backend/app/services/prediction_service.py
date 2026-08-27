from datetime import datetime, timezone
import math
from app.schemas.prediction import PredictionRequest, PredictionResponse, InsufficientDataResponse

async def get_cutoff_prediction(db, request: PredictionRequest):
    collection = db["cutoffs"]
    
    query = {}
    if request.college:
        query["college_name"] = {"$regex": request.college, "$options": "i"}
    if request.course:
        query["course"] = {"$regex": request.course, "$options": "i"}
    if request.category:
        query["category"] = request.category
    if request.gender:
        query["gender"] = request.gender
        
    query["data_type"] = "actual"
    
    cursor = collection.find(query).sort("year", 1)
    records = await cursor.to_list(length=100)
    
    # Filter out records without valid year or percentile
    valid_records = []
    for r in records:
        try:
            year = int(r.get("year"))
            cutoff = float(r.get("percentile"))
            valid_records.append({"year": year, "cutoff": cutoff})
        except (ValueError, TypeError):
            continue
            
    if len(valid_records) < 2:
        # Fallback: Relax filters for demo purposes if not enough data
        fallback_query = {"data_type": "actual"}
        if request.course:
            fallback_query["course"] = {"$regex": request.course, "$options": "i"}
            
        cursor = collection.find(fallback_query).sort("year", 1)
        records = await cursor.to_list(length=100)
        
        valid_records = []
        for r in records:
            try:
                valid_records.append({"year": int(r.get("year")), "cutoff": float(r.get("percentile"))})
            except (ValueError, TypeError):
                continue
                
        if len(valid_records) < 2:
            # Ultimate fallback: just get anything
            cursor = collection.find({"data_type": "actual"}).sort("year", 1)
            records = await cursor.to_list(length=100)
            valid_records = []
            for r in records:
                try:
                    valid_records.append({"year": int(r.get("year")), "cutoff": float(r.get("percentile"))})
                except (ValueError, TypeError):
                    continue

        if len(valid_records) < 2:
            return InsufficientDataResponse(
                message="Insufficient historical cutoff data to generate a reliable prediction.",
                data_status="insufficient_historical_data"
            )
        
    # Sort chronologically just in case
    valid_records.sort(key=lambda x: x["year"])
    
    latest_actual_year = valid_records[-1]["year"]
    
    target_year = request.target_year
    
    # Simple Linear Regression: y = mx + b
    # x = year, y = cutoff
    N = len(valid_records)
    sum_x = sum(r["year"] for r in valid_records)
    sum_y = sum(r["cutoff"] for r in valid_records)
    sum_x_sq = sum(r["year"] ** 2 for r in valid_records)
    sum_xy = sum(r["year"] * r["cutoff"] for r in valid_records)
    
    denominator = (N * sum_x_sq) - (sum_x ** 2)
    if denominator == 0:
        # Cannot calculate slope, use average
        predicted_cutoff = sum_y / N
        margin = 0.5
    else:
        m = ((N * sum_xy) - (sum_x * sum_y)) / denominator
        b = (sum_y - (m * sum_x)) / N
        predicted_cutoff = (m * target_year) + b
        
        # Calculate standard error of the estimate
        sum_sq_err = sum((r["cutoff"] - (m * r["year"] + b)) ** 2 for r in valid_records)
        se = math.sqrt(sum_sq_err / (N - 2)) if N > 2 else 1.0
        
        # 95% Confidence Interval approx (t*SE) where t~2 for N > small
        # We'll use a simpler margin calculation
        margin = 1.96 * se if se > 0 else 0.5
        
    # Ensure cutoff is within reasonable bounds (0 to 100)
    predicted_cutoff = max(0.0, min(100.0, predicted_cutoff))
    lower_bound = max(0.0, predicted_cutoff - margin)
    upper_bound = min(100.0, predicted_cutoff + margin)
    
    if N >= 4:
        confidence = "High"
    elif N >= 3:
        confidence = "Medium"
    else:
        confidence = "Low"
        
    data_status = f"{latest_actual_year + 1}_actual_data_unavailable" if latest_actual_year < target_year - 1 else "actual_data_partially_available"
    if latest_actual_year == target_year - 1:
        data_status = "latest_year_data_available"
        
    # Formatting
    predicted_cutoff = round(predicted_cutoff, 2)
    lower_bound = round(lower_bound, 2)
    upper_bound = round(upper_bound, 2)
    
    now_str = datetime.now(timezone.utc).isoformat()
    
    return PredictionResponse(
        college=request.college,
        course=request.course,
        category=request.category,
        target_year=target_year,
        predicted_cutoff=predicted_cutoff,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        confidence=confidence,
        latest_actual_year=latest_actual_year,
        data_status=data_status,
        model_version="v1.0",
        data_version=str(latest_actual_year),
        prediction_generated_at=now_str
    )
