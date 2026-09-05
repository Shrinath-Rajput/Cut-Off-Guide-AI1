from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Legacy Cutoff Schemas (kept for backwards compatibility)
class CutoffSearchRequest(BaseModel):
    percentile: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    university: Optional[str] = None
    course: Optional[str] = None
    location: Optional[str] = None
    round: Optional[str] = None

class CutoffResult(BaseModel):
    cutoff: str
    rank: str
    suggestion: str


# ML Percentile Prediction Schemas
class PercentilePredictRequest(BaseModel):
    exam: str = Field(..., description="Exam name: 'MHT-CET', 'JEE Main', or 'JEE Advanced'")
    marks: float = Field(..., description="Expected marks obtained in the exam")

class PercentilePredictResponse(BaseModel):
    exam: str
    marks: float
    max_marks: int
    predicted_percentile: float
    percentile_range: str
    estimated_rank: str
    performance_tier: str
    advisory_message: Optional[str] = None


# LLM College Recommendation Schemas
class CollegePredictLLMRequest(BaseModel):
    exam: str = Field("MHT-CET", description="Entrance Exam")
    marks: Optional[float] = Field(None, description="Marks scored (optional if percentile provided)")
    percentile: float = Field(..., description="Predicted or scored percentile (0.0 - 100.0)")
    category: str = Field("Open/General", description="Quota category: Open, OBC, SC, ST, EWS, TFWS, etc.")
    location: Optional[str] = Field(None, description="Preferred location/city: Pune, Mumbai, Nagpur, etc.")
    round: str = Field("Round 1", description="CAP Admission Round: Round 1, Round 2, Round 3")
    preferred_courses: Optional[List[str]] = Field(
        default=["Computer Science & Engineering"],
        description="List of target courses/branches"
    )

class CollegeRecommendationItem(BaseModel):
    college_id: str
    college_name: str
    city: str
    location: str
    branch: str
    cutoff_percentile: float
    chance_tier: str  # "Safe", "Target", "Ambitious"
    chance_percentage: int
    category: str
    round: str
    placement_avg: str
    highest_package: str
    fee_display: str
    ai_reasoning: str

class CollegePredictLLMResponse(BaseModel):
    summary: Dict[str, Any]
    colleges: List[CollegeRecommendationItem]
