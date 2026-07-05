import datetime
from typing import List, Dict, Any, Optional
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class AbsenteeRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.absentees)

    async def get_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        try:
            return await self.find_all({"studentId": ObjectId(student_id)}, sort_by="date", descending=True)
        except Exception:
            return []

    async def check_existence(self, student_id: str, date: datetime.datetime) -> bool:
        try:
            # Match date neglecting time components (start of day to end of day)
            start_of_day = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
            end_of_day = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
            
            existing = await self.find_one({
                "studentId": ObjectId(student_id),
                "date": {"$gte": start_of_day, "$lte": end_of_day}
            })
            return existing is not None
        except Exception:
            return False

    async def get_department_absentees(self, student_ids: List[str]) -> List[Dict[str, Any]]:
        if not student_ids:
            return []
        try:
            obj_ids = [ObjectId(sid) for sid in student_ids]
            return await self.find_all({"studentId": {"$in": obj_ids}}, sort_by="date", descending=True)
        except Exception:
            return []
