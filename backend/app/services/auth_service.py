import datetime
from typing import Optional, Dict, Any
from bson.objectid import ObjectId
from fastapi import HTTPException, status

from ..repositories.user import UserRepository
from ..repositories.student import StudentRepository
from ..schemas.auth import UserRegister, UserLogin, Token, UserOut
from ..core.password import get_password_hash, verify_password
from ..core.jwt import create_access_token, create_refresh_token, decode_token

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.student_repo = StudentRepository()

    async def register_user(self, user_in: UserRegister) -> Dict[str, Any]:
        # 1. Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # 2. Hash password and prepare user document
        hashed_password = get_password_hash(user_in.password)
        user_dict = {
            "fullName": user_in.fullName,
            "email": user_in.email,
            "phone": user_in.phone,
            "password": hashed_password,
            "role": user_in.role,
            "departmentId": ObjectId(user_in.departmentId) if user_in.departmentId else None,
            "status": "Active"
        }

        # 3. Save User
        user_id = await self.user_repo.create(user_dict)

        # 4. If Student role, initialize standard student sub-profile document
        if user_in.role == "Student":
            student_dict = {
                "registerNo": f"REG-{user_id[-6:].upper()}", # autogenerate registration reference for safety
                "enrollNo": f"ENR-{user_id[-6:].upper()}",
                "fullName": user_in.fullName,
                "program": "B.Tech",
                "departmentName": "Department of CS" if user_in.departmentId else "Unassigned",
                "userId": ObjectId(user_id),
                "departmentId": ObjectId(user_in.departmentId) if user_in.departmentId else None,
                "year": 1,
                "semester": 1,
                "section": "A",
                "attendancePercentage": 100.0,
                "totalFine": 0.0
            }
            await self.student_repo.create(student_dict)

        return {
            "id": user_id,
            "email": user_in.email,
            "fullName": user_in.fullName,
            "role": user_in.role
        }

    async def authenticate_user(self, login_in: UserLogin) -> Token:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check for temporary lockout
        lockout_until = user.get("lockoutUntil")
        if lockout_until:
            if lockout_until > datetime.datetime.utcnow():
                diff = lockout_until - datetime.datetime.utcnow()
                minutes = int(diff.total_seconds() / 60) + 1
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account is temporarily locked due to multiple failed login attempts. Try again in {minutes} minutes."
                )

        if not verify_password(login_in.password, user["password"]):
            # Increment failed attempts
            failed_attempts = user.get("failedLoginAttempts", 0) + 1
            updates = {"failedLoginAttempts": failed_attempts}
            
            if failed_attempts >= 5:
                updates["lockoutUntil"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                updates["failedLoginAttempts"] = 0
                await self.user_repo.update(str(user["_id"]), updates)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Incorrect password. Your account has been temporarily locked for 5 minutes."
                )
            else:
                await self.user_repo.update(str(user["_id"]), updates)
                remaining = 5 - failed_attempts
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Incorrect email or password. {remaining} login attempts remaining before lockout."
                )

        # Clear login lock states on success
        if user.get("failedLoginAttempts", 0) > 0 or user.get("lockoutUntil"):
            await self.user_repo.update(str(user["_id"]), {
                "failedLoginAttempts": 0,
                "lockoutUntil": None
            })

        if user.get("status") != "Active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive account. Please contact your administrator."
            )

        user_id_str = str(user["_id"])
        access_token = create_access_token(subject=user_id_str, role=user["role"])
        refresh_token = create_refresh_token(subject=user_id_str)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_access_token(self, refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.get("status") != "Active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        new_access_token = create_access_token(subject=user_id, role=user["role"])
        return new_access_token
