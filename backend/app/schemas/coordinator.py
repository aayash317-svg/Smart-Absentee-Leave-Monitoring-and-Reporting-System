from pydantic import BaseModel
from typing import Optional

class MarkAbsent(BaseModel):
    studentId: str
    date: str  # YYYY-MM-DD
    reason: Optional[str] = "Absent"
    status: str = "Unexcused" # Unexcused, Excused

class LeaveAction(BaseModel):
    action: str  # approve, reject
    reason: Optional[str] = None
