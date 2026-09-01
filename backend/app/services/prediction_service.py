from datetime import datetime, timezone
import math
from app.schemas.prediction import PredictionRequest, PredictionResponse, InsufficientDataResponse

def _calculate_prediction(valid_records, target_year):
    N = len(valid_records)
    sum_x = sum(r["year"] for r in valid_records)
    sum_y = sum(r["cutoff"] for r in valid_records)
    sum_x_sq = sum(r["year"] ** 2 for r in valid_records)
    sum_xy = sum(r["year"] * r["cutoff"] for r in valid_records)
    
    denominator = (N * sum_x_sq) - (sum_x ** 2)
    if denominator == 0:
        predicted_cutoff = sum_y / N
        margin = 0.5
    else:
        m = ((N * sum_xy) - (sum_x * sum_y)) / denominator
        b = (sum_y - (m * sum_x)) / N
        predicted_cutoff = (m * target_year) + b
        
        sum_sq_err = sum((r["cutoff"] - (m * r["year"] + b)) ** 2 for r in valid_records)
        se = math.sqrt(sum_sq_err / (N - 2)) if N > 2 else 1.0
        
        margin = 1.96 * se if se > 0 else 0.5
        
    predicted_cutoff = max(0.0, min(100.0, predicted_cutoff))
    lower_bound = max(0.0, predicted_cutoff - margin)
    upper_bound = min(100.0, predicted_cutoff + margin)
    
    if N >= 4:
        confidence = "High"
    elif N >= 3:
        confidence = "Medium"
    else:
        confidence = "Low"
        
    return round(predicted_cutoff, 2), round(lower_bound, 2), round(upper_bound, 2), confidence

async def get_cutoff_prediction(db, request: PredictionRequest):
    collection = db["cutoffs"]
    
    query = {"data_type": "actual"}
    if request.course:
        query["course"] = {"$regex": request.course, "$options": "i"}
    if request.category:
        query["category"] = request.category
    if request.gender:
        query["gender"] = request.gender
    if request.college:
        query["college_name"] = {"$regex": request.college, "$options": "i"}
        
    now_str = datetime.now(timezone.utc).isoformat()
    
    cursor = collection.find(query)
    records = await cursor.to_list(length=1000)
    
    college_data = {}
    latest_actual_year = 0
    for r in records:
        cname = r.get("college_name")
        if not cname:
            continue
        try:
            year = int(r["year"])
            cutoff = float(r["percentile"])
            latest_actual_year = max(latest_actual_year, year)
        except (ValueError, TypeError, KeyError):
            continue
            
        if cname not in college_data:
            college_data[cname] = []
        college_data[cname].append({"year": year, "cutoff": cutoff})
        
    recommended_colleges = []
    for cname, v_records in college_data.items():
        if not v_records:
            continue
        v_records.sort(key=lambda x: x["year"])
        
        predicted_cutoff, lower_bound, upper_bound, confidence = _calculate_prediction(v_records, request.target_year)
        
        match_probability = "Low"
        if request.score is not None:
            if request.score >= predicted_cutoff:
                match_probability = "High"
            elif request.score >= lower_bound:
                match_probability = "Medium"
                
        recommended_colleges.append({
            "college_name": cname,
            "predicted_cutoff": predicted_cutoff,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence": confidence,
            "match_probability": match_probability
        })
            
    recommended_colleges.sort(key=lambda x: x["predicted_cutoff"], reverse=True)
    
    if not recommended_colleges:
         return InsufficientDataResponse(
            message="No historical cutoff data found for this specific combination of course, category, gender, and college search.",
            data_status="insufficient_historical_data"
        )

    if latest_actual_year == 0:
        latest_actual_year = datetime.now().year - 1
        
    data_status = "college_recommendations"
    
    return PredictionResponse(
        college=request.college,
        course=request.course,
        category=request.category,
        target_year=request.target_year,
        latest_actual_year=latest_actual_year,
        data_status=data_status,
        model_version="v1.0",
        data_version="mixed",
        prediction_generated_at=now_str,
        recommended_colleges=recommended_colleges
    )
