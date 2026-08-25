from pydantic import BaseModel, Field
from typing import Optional, List

class ProfileBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    userType: Optional[str] = None
    goals: Optional[List[str]] = None
    dob: Optional[str] = None
    exam: Optional[str] = None
    percentile: Optional[str] = None
    category: Optional[str] = None
    domicile: Optional[str] = None
    locationZone: Optional[str] = None
    examScore: Optional[str] = None
    careerOption: Optional[str] = None
    preferredBranch: Optional[str] = None
    educationLevel: Optional[str] = None
    targetStream: Optional[str] = None
    subjects: Optional[List[str]] = None
    areasOfInterest: Optional[List[str]] = None
    targetDegreeLevel: Optional[str] = None
    expectedEntranceScore: Optional[str] = None
    preferredLocation: Optional[str] = None
    budgetRange: Optional[str] = None
    pwdCrossCategory: Optional[bool] = None
    collegeType: Optional[str] = None
    hostelRequired: Optional[bool] = None

class ProfileCreate(ProfileBase):
    uid: str

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: str
    uid: str
