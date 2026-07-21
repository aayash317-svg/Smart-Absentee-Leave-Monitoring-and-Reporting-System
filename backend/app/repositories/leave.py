from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class LeaveRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.leaveApplications)

    async def get_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        s_ids = [student_id]
        try:
            s_ids.append(ObjectId(student_id))
        except Exception:
            pass
        try:
            s_ids.append(str(student_id))
        except Exception:
            pass
        return await self.find_all({"studentId": {"$in": s_ids}}, sort_by="startDate", descending=True)

    async def get_pending_leaves_by_students(self, student_ids: List[str]) -> List[Dict[str, Any]]:
        if not student_ids:
            return []
        ids_flat = []
        for sid in student_ids:
            ids_flat.append(sid)
            try:
                ids_flat.append(ObjectId(sid))
            except Exception:
                pass
        return await self.find_all({
            "studentId": {"$in": ids_flat},
            "status": "Pending"
        }, sort_by="appliedDate", descending=True)
            
    async def get_pending_leaves(self) -> List[Dict[str, Any]]:
        return await self.find_all({"status": "Pending"}, sort_by="appliedDate", descending=True)
