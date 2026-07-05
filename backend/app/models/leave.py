"""
Leave Application Document Model.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LeaveApplicationDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    studentId: str  # References Student
    startDate: datetime
    endDate: datetime
    reason: str
    status: str = "Pending"  # Pending, Approved, Rejected
    approvedBy: Optional[str] = None  # References User
    comments: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
