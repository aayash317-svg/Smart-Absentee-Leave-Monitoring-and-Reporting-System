import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., description="Password must follow strong password guidelines")
    fullName: str = Field(..., min_length=2)
    phone: str
    role: str = Field("Student", description="Student, Coordinator, HOD, Dean, Admin")
    departmentId: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase character (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase character (a-z)")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one numerical digit (0-9)")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special symbol")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    role: str
    type: str
    exp: int

class UserOut(BaseModel):
    id: str
    email: EmailStr
    fullName: str
    phone: str
    role: str
    status: str
    departmentId: Optional[str] = None

    class Config:
        from_attributes = True
