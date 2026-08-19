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
    email: Optional[str] = None
    phone: Optional[str] = None
    uid: Optional[str] = None
    name: Optional[str] = None
    provider: Optional[str] = "phone"
    photoURL: Optional[str] = None
