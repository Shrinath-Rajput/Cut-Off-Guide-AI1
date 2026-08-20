from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    provider: str = "phone"
    photoURL: Optional[str] = None
    role: str = "USER"

class UserCreate(UserBase):
    uid: Optional[str] = None

class UserInDB(UserBase):
    id: str
    uid: str
    createdAt: datetime
    lastLogin: datetime

class UserResponse(UserBase):
    id: str
    uid: str
    createdAt: datetime
    lastLogin: datetime
    
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserSignup(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=254)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8, max_length=128)
    category: Optional[str] = None
    pwdCrossCategory: Optional[bool] = None
    domicile: Optional[str] = None
    exam: Optional[str] = None
    examScore: Optional[str] = None
    careerOption: Optional[str] = None
    preferredBranch: Optional[str] = None
    preferredLocation: Optional[str] = None
    budgetRange: Optional[str] = None
    collegeType: Optional[str] = None
    hostelRequired: Optional[bool] = None

class LoginOtpRequest(BaseModel):
    uid: str
    phone: str
    name: Optional[str] = ""
    email: Optional[str] = ""

class LoginOtpVerifyRequest(LoginOtpRequest):
    otp: str
    sessionId: str
