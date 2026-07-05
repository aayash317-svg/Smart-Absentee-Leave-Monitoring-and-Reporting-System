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
    createdAt: datetime = Field(default_factory=datetime.utcnow)
