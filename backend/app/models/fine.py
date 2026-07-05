from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FinePaymentModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    studentId: str
    leaveApplicationId: str
    amount: float
    status: str = "Unpaid"  # Unpaid, Paid
    receiptNo: Optional[str] = None
    paymentMode: Optional[str] = None  # Online, Cash
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    paymentDate: Optional[datetime] = None
    isDeleted: bool = False
