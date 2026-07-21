from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from .base import BaseRepository
from ..database.connection import get_db

class StudentRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.students)

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not user_id:
            return None
        res = await self.find_one({"userId": str(user_id)})
        if not res:
            try:
                res = await self.find_one({"userId": ObjectId(user_id)})
            except Exception:
                pass
        return res

    async def get_by_register_no(self, reg_no: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"registerNo": reg_no})

    async def search_students(self, query: str = None, department_id: str = None) -> List[Dict[str, Any]]:
        filter_dict = {}
        if department_id:
            try:
                filter_dict["departmentId"] = ObjectId(department_id)
            except Exception:
                pass
        
        if query:
            filter_dict["$or"] = [
                {"fullName": {"$regex": query, "$options": "i"}},
                {"registerNo": {"$regex": query, "$options": "i"}},
                {"enrollNo": {"$regex": query, "$options": "i"}}
            ]
            
        return await self.find_all(filter_dict)
