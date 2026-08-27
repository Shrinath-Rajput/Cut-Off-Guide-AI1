from typing import Optional, List
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    college: str
    course: str
    category: Optional[str] = None
    gender: Optional[str] = None
    target_year: int = 2027

class PredictionResponse(BaseModel):
    college: str
    course: str
    category: Optional[str]
    target_year: int
    predicted_cutoff: float
    lower_bound: float
    upper_bound: float
    confidence: str
    latest_actual_year: Optional[int]
    data_status: str
    model_version: str
    data_version: str
    prediction_generated_at: str
    
class InsufficientDataResponse(BaseModel):
    message: str
    data_status: str
