from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    registerNo: str
    enrollNo: str
    fullName: str
    program: str
    departmentName: str
    userId: str
    departmentId: str
    year: int
    semester: int
    section: str
    attendancePercentage: float = 100.0
    totalFine: float = 0.0
    isDeleted: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
