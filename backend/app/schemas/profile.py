from pydantic import BaseModel, Field
from typing import Optional

class ProfileBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    exam: Optional[str] = None
    percentile: Optional[str] = None
    category: Optional[str] = None
    domicile: Optional[str] = None
    examScore: Optional[str] = None
    preferredBranch: Optional[str] = None
    preferredLocation: Optional[str] = None
    budgetRange: Optional[str] = None

class ProfileCreate(ProfileBase):
    uid: str

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: str
    uid: str
