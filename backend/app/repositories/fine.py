from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class FineRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.fine_transactions)
        self.rules_collection = db.fine_rules

    async def get_active_rules(self) -> Optional[Dict[str, Any]]:
        # Fetch first active rule document
        return await self.rules_collection.find_one({})

    async def create_rule(self, rules_data: Dict[str, Any]) -> str:
        # Clear existing rules first to maintain single active config
        await self.rules_collection.delete_many({})
        result = await self.rules_collection.insert_one(rules_data)
        return str(result.inserted_id)

    async def get_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        try:
            return await self.find_all({"studentId": ObjectId(student_id)}, sort_by="createdAt", descending=True)
        except Exception:
            return []
            
    async def get_pending_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        try:
            return await self.find_all({
                "studentId": ObjectId(student_id),
                "status": "Pending"
            })
        except Exception:
            return []
