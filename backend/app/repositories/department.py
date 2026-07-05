from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class DepartmentRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.departments)

    async def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"departmentCode": code})

    async def get_by_hod(self, hod_id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.find_one({"hodId": ObjectId(hod_id)})
        except Exception:
            return None
