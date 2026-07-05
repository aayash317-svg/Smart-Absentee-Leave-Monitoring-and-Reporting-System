from typing import Optional, Dict, Any
from .base import BaseRepository
from ..database.connection import get_db

class UserRepository(BaseRepository):
    def __init__(self):
        db = get_db()
        super().__init__(db.users)

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"email": email})
