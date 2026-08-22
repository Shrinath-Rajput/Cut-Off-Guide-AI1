from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field

class CollegeBase(BaseModel):
    id: str
    name: str
    rank: Optional[int] = 1
    nirf_rank: Optional[int] = None
    rating: Optional[Union[str, float, int]] = "4.5"
    city: Optional[str] = None
    state: Optional[str] = "India"
    location: Optional[str] = None
    courses: Optional[List[str]] = Field(default_factory=list)
    exams: Optional[List[str]] = Field(default_factory=list)
    feeLabel: Optional[str] = None
    fee_display: Optional[str] = None
    feeValue: Optional[int] = None
    cutoff: Optional[str] = None
    type: Optional[str] = "Engineering Institute"
    image: Optional[str] = None
    acceptanceRate: Optional[str] = None
    averagePackage: Optional[str] = None
    placement_avg: Optional[str] = None
    highestPackage: Optional[str] = None
    highest_package: Optional[str] = None
    top_recruiters: Optional[List[str]] = Field(default_factory=list)
    highlights: Optional[str] = None
    website: Optional[str] = None

class CollegeResponse(CollegeBase):
    pass

class PaginatedCollegeResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[CollegeResponse]
