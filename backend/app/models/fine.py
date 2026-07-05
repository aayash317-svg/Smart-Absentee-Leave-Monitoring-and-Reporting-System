"""
Fine and Fine Rule Document Models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FineRuleDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    minAttendance: float = 75.0
    fineAmountPerDay: float = 100.0
    graceDays: int = 3
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class FinePaymentDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    studentId: str  # References Student
    amount: float
    paymentDate: Optional[datetime] = None
    paymentMode: Optional[str] = None  # Online, Cash
    status: str = "Pending"  # Pending, Paid
    receiptNo: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
