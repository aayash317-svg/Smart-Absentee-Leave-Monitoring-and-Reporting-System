from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class LeaveRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.leave_applications)

    async def get_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        try:
            return await self.find_all({"studentId": ObjectId(student_id)}, sort_by="startDate", descending=True)
        except Exception:
            return []

    async def get_pending_leaves_by_students(self, student_ids: List[str]) -> List[Dict[str, Any]]:
        if not student_ids:
            return []
        try:
            obj_ids = [ObjectId(sid) for sid in student_ids]
            return await self.find_all({
                "studentId": {"$in": obj_ids},
                "status": "Pending"
            }, sort_by="appliedDate", descending=True)
        except Exception:
            return []
            
    async def get_pending_leaves(self) -> List[Dict[str, Any]]:
        return await self.find_all({"status": "Pending"}, sort_by="appliedDate", descending=True)
