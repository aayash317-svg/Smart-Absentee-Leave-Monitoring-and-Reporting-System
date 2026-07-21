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

    async def search_students(self, query: str = None, department_id: str = None, department_code: str = None) -> List[Dict[str, Any]]:
        conditions = []
        
        if department_id or department_code:
            or_dept = []
            if department_id:
                dept_matches = [department_id, str(department_id)]
                try:
                    dept_matches.append(ObjectId(department_id))
                except Exception:
                    pass
                or_dept.append({"departmentId": {"$in": dept_matches}})
                
            if department_code:
                or_dept.append({"department": department_code})
            elif isinstance(department_id, str) and not ObjectId.is_valid(department_id):
                or_dept.append({"department": department_id})
                
            if len(or_dept) == 1:
                conditions.append(or_dept[0])
            elif len(or_dept) > 1:
                conditions.append({"$or": or_dept})
        
        if query:
            conditions.append({
                "$or": [
                    {"fullName": {"$regex": query, "$options": "i"}},
                    {"registerNo": {"$regex": query, "$options": "i"}},
                    {"enrollNo": {"$regex": query, "$options": "i"}},
                    {"id": {"$regex": query, "$options": "i"}}
                ]
            })
            
        if not conditions:
            filter_dict = {}
        elif len(conditions) == 1:
            filter_dict = conditions[0]
        else:
            filter_dict = {"$and": conditions}
            
        return await self.find_all(filter_dict)
