from pydantic import BaseModel
from typing import Optional, List
import datetime

class LeaveApply(BaseModel):
    startDate: str  # YYYY-MM-DD
    endDate: str    # YYYY-MM-DD
    leaveType: str  # Hour Leave, FN Leave, AN Leave, Full Day Leave, Multiple Day Leave
    reason: str
    certificateUrl: Optional[str] = None

class LeaveOut(BaseModel):
    id: str
    startDate: str
    endDate: str
    leaveType: str
    reason: str
    certificateUrl: Optional[str] = None
    status: str
    appliedDate: str

class AbsenteeOut(BaseModel):
    id: str
    date: str
    reason: str
    status: str

class FineOut(BaseModel):
    id: str
    amount: float
    status: str
    receiptNo: Optional[str] = None
    createdAt: str
    paymentDate: Optional[str] = None

class StudentProfile(BaseModel):
    registerNo: str
    enrollNo: str
    fullName: str
    program: str
    departmentName: str
    year: int
    semester: int
    section: str
    attendancePercentage: float
    totalFine: float
