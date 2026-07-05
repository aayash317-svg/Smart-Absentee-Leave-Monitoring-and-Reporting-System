from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    fullName: str
    email: EmailStr
    phone: str
    password: str  # Hashed bcrypt password
    role: str      # Student, Coordinator, HOD, Dean, Admin
    departmentId: Optional[str] = None
    status: str = "Active"  # Active, Deactivated
    failedLoginAttempts: int = 0
    lockoutUntil: Optional[datetime] = None
    isDeleted: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
