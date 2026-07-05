from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class ClassRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.classes)

    async def get_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        try:
            return await self.find_all({"departmentId": ObjectId(department_id)})
        except Exception:
            return []

    async def get_by_coordinator(self, coordinator_id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.find_one({"coordinatorId": ObjectId(coordinator_id)})
        except Exception:
            return None
