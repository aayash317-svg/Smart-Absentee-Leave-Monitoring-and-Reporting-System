import datetime
from typing import Dict, Any, Optional
from bson.objectid import ObjectId

from ..repositories.fine import FineRepository
from ..core.config import settings

class FineService:
    def __init__(self):
        self.fine_repo = FineRepository()

    async def calculate_delay_fine(self, absent_date: datetime.datetime, applied_date: datetime.datetime) -> float:
        # Calculate difference in days
        delta = applied_date.date() - absent_date.date()
        delay_days = max(0, delta.days)
        
        # Fetch active fine rules from DB
        rules_doc = await self.fine_repo.get_active_rules()
        rules = rules_doc.get("rules", settings.DEFAULT_FINE_RULES) if rules_doc else settings.DEFAULT_FINE_RULES
        
        # Calculate fine
        delay_str = str(delay_days)
        if delay_str in rules:
            return float(rules[delay_str])
        else:
            # Over 4 days -> progressive cap of ₹80 + delay surcharge
            max_defined_days = max(int(k) for k in rules.keys())
            max_defined_fine = float(rules[str(max_defined_days)])
            surcharge = (delay_days - max_defined_days) * 20.0
            return max_defined_fine + surcharge

    async def generate_fine_transaction(self, student_id: str, leave_app_id: str, amount: float) -> Optional[str]:
        if amount <= 0:
            return None
            
        transaction_data = {
            "studentId": ObjectId(student_id),
            "leaveApplicationId": ObjectId(leave_app_id),
            "amount": amount,
            "paymentDate": None,
            "paymentMode": None,
            "status": "Pending",
            "receiptNo": None,
            "createdAt": datetime.datetime.utcnow()
        }
        
        tx_id = await self.fine_repo.create(transaction_data)
        return tx_id
