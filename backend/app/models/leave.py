from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LeaveApplicationModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    studentId: str
    startDate: datetime
    endDate: datetime
    leaveType: str  # Hour Leave, FN Leave, AN Leave, Full Day Leave, Multiple Day Leave
    reason: str
    certificateUrl: Optional[str] = None
    status: str = "Pending"  # Pending, Approved, Rejected
    appliedDate: datetime = Field(default_factory=datetime.utcnow)
    approvedBy: Optional[str] = None  # User ID of HOD/Coordinator who approved/rejected
    rejectionReason: Optional[str] = None
    isDeleted: bool = False
