from typing import List, Optional
from pydantic import BaseModel

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
