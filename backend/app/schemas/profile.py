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
    subjects: Optional[List[str]] = Field(None, max_length=1)
    areasOfInterest: Optional[List[str]] = Field(None, max_length=1)
    targetDegreeLevel: Optional[str] = None
    expectedEntranceScore: Optional[str] = None
    preferredLocation: Optional[str] = None
    budgetRange: Optional[str] = None
    pwdCrossCategory: Optional[bool] = None
    collegeType: Optional[str] = None
    hostelRequired: Optional[bool] = None
    scoreType: Optional[str] = None

    from pydantic import model_validator
    @model_validator(mode='after')
    def validate_score(self) -> 'ProfileBase':
        if self.examScore and getattr(self, 'scoreType', None):
            try:
                num = float(self.examScore)
                if num < 0:
                    raise ValueError("Score cannot be negative")
                if self.scoreType == 'Percentage' and num > 100:
                    raise ValueError("Percentage cannot exceed 100")
                if self.scoreType == 'CGPA' and num > 10:
                    raise ValueError("CGPA cannot exceed 10")
            except ValueError as e:
                raise ValueError(str(e))
        return self

class ProfileCreate(ProfileBase):
    uid: str

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: str
    uid: str
