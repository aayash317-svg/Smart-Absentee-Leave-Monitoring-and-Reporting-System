"""
Student Document Model.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    userId: str  # References User
    fullName: str
    registerNo: str
    enrollNo: str
    program: str
    departmentId: str
    departmentName: str
    year: int
    semester: int
    section: str
    attendancePercentage: float = 100.0
    totalClasses: int = 0
    classesAttended: int = 0
    totalFine: float = 0.0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
