"""
FastAPI dependencies module.
Provides auth checks, token decoding, and current user extraction.
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional, List
from bson.objectid import ObjectId

from ..core.jwt import decode_access_token, safe_object_id
from ..database.connection import get_db

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Dependency that returns the current authenticated user's ID string."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
        
    try:
        parts = authorization.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        token = parts[1]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
        
    payload = decode_access_token(token)
    return payload["sub"]

async def get_current_user(user_id: str = Depends(get_current_user_id)) -> dict:
    """Dependency that returns the complete user dict from database."""
    db = get_db()
    user = await db.users.find_one({"_id": safe_object_id(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    if user.get("status") != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
        
    user["id"] = str(user["_id"])
    return user

class RoleChecker:
    """Role-based access guard dependency."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
        
    def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action not permitted for your role scope"
            )
        return current_user
