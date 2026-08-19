from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SavedCollegeBase(BaseModel):
    college_id: str
    name: str
    location: str
    course: Optional[str] = None
    cutoff: Optional[str] = None
    rank: Optional[str] = None
    rating: Optional[str] = None
    image: Optional[str] = None

class SavedCollegeCreate(SavedCollegeBase):
    pass

class SavedCollegeResponse(SavedCollegeBase):
    id: str
    uid: str
    savedOn: datetime
