from fastapi import Depends, HTTPException, status, Header
from typing import Optional, List
from bson.objectid import ObjectId

from ..core.security import decode_token
from ..repositories.user import UserRepository

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
        
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
        
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )
        
    user_id = payload.get("sub")
    user_repo = UserRepository()
    user = await user_repo.get_by_id(user_id)
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
        
    # Serialize ID
    user["id"] = str(user["_id"])
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action not permitted for your role scope"
            )
        return current_user
