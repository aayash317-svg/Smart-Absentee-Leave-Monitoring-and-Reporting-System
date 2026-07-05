import jwt
import datetime
from typing import Union, Any, Optional
from bson.objectid import ObjectId, InvalidId
from fastapi import HTTPException, status
from .config import settings

def create_access_token(
    subject: Union[str, Any], 
    role: str, 
    email: str = "", 
    expires_delta: Optional[datetime.timedelta] = None
) -> str:
    """Create a signed JWT access token. Supports subject parameter and email."""
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "email": email,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create a longer-lived refresh token."""
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    payload = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    """Safely decode a JWT token. Returns None on validation failure."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token. Raises HTTP 401 on validation failure."""
    payload = decode_token(token)
    if not payload or payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has been tampered with"
        )
    return payload

def safe_object_id(value: str) -> ObjectId:
    """Convert string to ObjectId safely. Raises HTTP 400 Bad Request on failure."""
    try:
        return ObjectId(value)
    except (InvalidId, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {value}"
        )
