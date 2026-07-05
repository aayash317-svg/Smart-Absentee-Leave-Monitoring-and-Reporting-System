from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AbsenteeModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    studentId: str
    date: datetime
    markedBy: str  # User ID of coordinator who marked
    status: str = "Unexcused"  # Unexcused, Excused
    leaveApplicationId: Optional[str] = None
    isDeleted: bool = False
