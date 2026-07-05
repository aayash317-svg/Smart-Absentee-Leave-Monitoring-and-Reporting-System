from typing import Generic, TypeVar, List, Dict, Any, Optional
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    def _clean_filter(self, filter: Dict[str, Any]) -> Dict[str, Any]:
        clean = filter.copy() if filter else {}
        clean["isDeleted"] = {"$ne": True}
        return clean

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.collection.find_one({"_id": ObjectId(id), "isDeleted": {"$ne": True}})
        except Exception:
            return None

    async def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one(self._clean_filter(filter))

    async def find_all(self, filter: Dict[str, Any] = {}, sort_by: str = None, descending: bool = False, limit: int = 0) -> List[Dict[str, Any]]:
        cursor = self.collection.find(self._clean_filter(filter))
        if sort_by:
            direction = -1 if descending else 1
            cursor = cursor.sort(sort_by, direction)
        if limit > 0:
            cursor = cursor.limit(limit)
            
        results = []
        async for doc in cursor:
            results.append(doc)
        return results

    async def create(self, data: Dict[str, Any]) -> str:
        # Defaults isDeleted to False on creation
        doc = data.copy()
        if "isDeleted" not in doc:
            doc["isDeleted"] = False
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, id: str, data: Dict[str, Any]) -> bool:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(id), "isDeleted": {"$ne": True}},
                {"$set": data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def delete(self, id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def soft_delete(self, id: str) -> bool:
        return await self.update(id, {"isDeleted": True})

    async def count(self, filter: Dict[str, Any] = {}) -> int:
        return await self.collection.count_documents(self._clean_filter(filter))
