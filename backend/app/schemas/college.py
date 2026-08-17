from typing import List, Optional
from pydantic import BaseModel

class CollegeBase(BaseModel):
    id: str
    rank: int
    name: str
    rating: str
    location: str
    courses: List[str]
    feeLabel: str
    feeValue: int
    cutoff: str
    type: str
    state: str
    image: str
    acceptanceRate: Optional[str] = None
    averagePackage: Optional[str] = None
    highestPackage: Optional[str] = None

class CollegeResponse(CollegeBase):
    pass

class PaginatedCollegeResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[CollegeResponse]
