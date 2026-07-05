import jwt
import datetime
import bcrypt
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from bson.objectid import ObjectId, InvalidId

from ..config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..db import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- SECURITY: In-memory brute-force rate limiter ---
# Tracks (ip -> [attempt_timestamps]) for login
_login_attempts: dict = defaultdict(list)
_MAX_ATTEMPTS = 5          # max failed logins
_WINDOW_SECONDS = 15 * 60  # within 15 minutes

def _check_rate_limit(ip: str):
    """Raise 429 if the IP has exceeded login attempt limit."""
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(seconds=_WINDOW_SECONDS)
    # Keep only recent attempts
    _login_attempts[ip] = [
        t for t in _login_attempts[ip] if t > cutoff
    ]
    if len(_login_attempts[ip]) >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please wait {_WINDOW_SECONDS // 60} minutes before trying again."
        )

def _record_failed_attempt(ip: str):
    _login_attempts[ip].append(datetime.datetime.utcnow())

def _clear_attempts(ip: str):
    _login_attempts.pop(ip, None)


# --- SECURITY: Safe ObjectId converter ---
def safe_object_id(value: str) -> ObjectId:
    """Convert string to ObjectId, raising 400 instead of crashing on invalid input."""
    try:
        return ObjectId(value)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {value}")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    # --- SECURITY FIX: Input length limits to prevent oversized payload attacks ---
    @field_validator('email')
    @classmethod
    def email_max_length(cls, v):
        if len(v) > 254:  # RFC 5321 max email length
            raise ValueError('Email address is too long')
        return v

    @field_validator('password')
    @classmethod
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 128:
            raise ValueError('Password is too long (max 128 characters)')
        return v

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    try:
        token_type, token = authorization.split(" ", 1)
        if token_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type, must be Bearer"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    # --- SECURITY FIX: Catch all JWT errors explicitly ---
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has been tampered with"
        )

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, request: Request):
    db = get_db()

    # --- SECURITY FIX: Brute-force rate limiting per client IP ---
    # This runs FIRST before any DB call so bots are blocked early.
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    user = db.users.find_one({"email": req.email})

    # --- SECURITY FIX: Constant-time password check (prevent email enumeration) ---
    # Use a pre-computed real bcrypt hash of a junk string as fallback.
    # This ensures bcrypt.checkpw() always runs for the same duration
    # whether or not the user account exists.
    # Generated with: bcrypt.hashpw(b"__dummy__", bcrypt.gensalt(12))
    _DUMMY_HASH = "$2b$12$eImiTXuWVxfM37uY4JANjQe5ps2zrPHERosOoXj4bLFcPcqtqXWom"
    stored_password = (user.get("password") or _DUMMY_HASH) if user else _DUMMY_HASH

    try:
        is_correct = bcrypt.checkpw(req.password.encode('utf-8'), stored_password.encode('utf-8'))
    except Exception:
        is_correct = False

    if not user or not is_correct:
        # Record failed attempt and raise a consistent error
        _record_failed_attempt(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if user.get("status") != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Clear failed attempts on successful login
    _clear_attempts(client_ip)

    # Generate token
    user_id_str = str(user["_id"])
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id_str, "role": user["role"], "email": user["email"]},
        expires_delta=access_token_expires
    )

    # Prepare user info response (exclude password)
    user_info = {
        "id": user_id_str,
        "fullName": user["fullName"],
        "email": user["email"],
        "phone": user["phone"],
        "role": user["role"],
        "status": user["status"],
        "departmentId": str(user["departmentId"]) if user.get("departmentId") else None
    }

    return {"access_token": access_token, "user": user_info}

@router.get("/me")
def get_me(user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_info = {
        "id": str(user["_id"]),
        "fullName": user["fullName"],
        "email": user["email"],
        "phone": user["phone"],
        "role": user["role"],
        "status": user["status"],
        "departmentId": str(user["departmentId"]) if user.get("departmentId") else None
    }

    # If the user is a student, also fetch student record
    if user["role"] == "Student":
        student = db.students.find_one({"userId": safe_object_id(user_id)})
        if student:
            user_info["studentDetails"] = {
                "id": str(student["_id"]),
                "registerNo": student["registerNo"],
                "enrollNo": student["enrollNo"],
                "program": student["program"],
                "departmentName": student["departmentName"],
                "year": student["year"],
                "semester": student["semester"],
                "section": student["section"],
                "attendancePercentage": student["attendancePercentage"],
                "totalFine": student["totalFine"]
            }

    return user_info
