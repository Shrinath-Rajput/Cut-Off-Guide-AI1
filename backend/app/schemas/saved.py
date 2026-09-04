from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

class SavedCollegeBase(BaseModel):
    college_id: Optional[str] = Field(None, alias="collegeId")
    name: str
    location: Optional[str] = "India"
    course: Optional[str] = None
    cutoff: Optional[str] = None
    rank: Optional[Union[str, int]] = None
    rating: Optional[Union[str, float, int]] = None
    image: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "ignore"

class SavedCollegeCreate(SavedCollegeBase):
    pass

class SavedCollegeResponse(SavedCollegeBase):
    id: str
    uid: str
    savedOn: Optional[datetime] = None
