"""
User Document Model.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    fullName: str
    phone: str
    password: str  # Hashed
    role: str      # Dean, HOD, Coordinator, Faculty, Student
    status: str    # Active, Deactivated
    departmentId: Optional[str] = None
    id_number: Optional[str] = None
    register_number: Optional[str] = None
    coordinator_id: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    is_verified: bool = True
    last_login: str = ""
    attendance_percentage: str = ""
    profile_image: str = ""
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
