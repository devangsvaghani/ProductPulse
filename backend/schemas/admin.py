from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    is_admin: bool = False

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    is_admin: Optional[bool] = None

class AnalyticsData(BaseModel):
    total_users: int
    total_uploads: int
    total_analysis_results: int
    uploads_by_status: Dict[str, int]