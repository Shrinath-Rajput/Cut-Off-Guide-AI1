from typing import Optional, List
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    college: Optional[str] = None
    course: str
    category: Optional[str] = None
    gender: Optional[str] = None
    target_year: int = 2027
    score: Optional[float] = None

class PredictionResponse(BaseModel):
    college: Optional[str] = None
    course: str
    category: Optional[str]
    target_year: int
    predicted_cutoff: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: Optional[str] = None
    latest_actual_year: Optional[int]
    data_status: str
    model_version: str
    data_version: str
    prediction_generated_at: str
    recommended_colleges: Optional[List[dict]] = None
    
class InsufficientDataResponse(BaseModel):
    message: str
    data_status: str
