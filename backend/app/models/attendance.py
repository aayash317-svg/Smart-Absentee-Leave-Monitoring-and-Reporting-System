"""
Attendance (Absentee) Document Model.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AbsenteeDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    studentId: str  # References Student
    date: datetime
    reason: Optional[str] = None
    status: str = "Unexcused"  # Unexcused, Excused, Pending Leave
    markedBy: str  # References User (Faculty/Staff)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
