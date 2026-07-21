from fastapi import APIRouter, Depends, status, Body, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime, secrets
from ..schemas.auth import UserRegister, UserLogin, Token, UserOut
from ..services.auth_service import AuthService
from ..core.password import hash_password, verify_password
from ..database.connection import get_db
from .deps import get_current_user

# In-memory token store (use Redis in production)
_reset_tokens: dict = {}

router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    return await auth_service.register_user(user_in)

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin):
    return await auth_service.authenticate_user(login_in)

@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    new_access_token = await auth_service.refresh_access_token(refresh_token)
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


class UpdateProfileRequest(BaseModel):
    phone: Optional[str] = None
    mobile: Optional[str] = None
    fullName: Optional[str] = None
    address: Optional[str] = None


@router.put("/me")
async def update_me(payload: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    """Update the authenticated user's own profile fields (phone, mobile, fullName, address)."""
    from bson.objectid import ObjectId
    db = get_db()
    update_fields: dict = {}

    phone_val = payload.phone or payload.mobile
    if phone_val:
        update_fields["phone"] = str(phone_val)
        update_fields["mobile"] = str(phone_val)
    if payload.fullName:
        update_fields["fullName"] = str(payload.fullName)
    if payload.address:
        update_fields["address"] = str(payload.address)

    if not update_fields:
        return {"message": "No fields to update"}

    update_fields["updatedAt"] = datetime.datetime.utcnow()
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": update_fields}
    )

    # Sync phone to students collection if this user is a student
    role = current_user.get("role", "")
    if role.lower() == "student":
        await db.students.update_one(
            {"$or": [{"userId": current_user["id"]}, {"userId": ObjectId(current_user["id"])}]},
            {"$set": update_fields}
        )

    return {"message": "Profile updated successfully", "updatedFields": list(update_fields.keys())}


# ── Password Reset Flow ───────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Generate a reset token for the given email address.
    In production this should send an actual email via notification_service."""
    db = get_db()
    user = await db.users.find_one({"email": req.email.lower().strip()})
    # Always return 200 to prevent user enumeration
    if user:
        token = secrets.token_urlsafe(32)
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        _reset_tokens[token] = {"user_id": str(user["_id"]), "expires": expires}
        # TODO: send email via notification_service.send_reset_email(user["email"], token)
        # For dev, return token in response (remove before production!)
        return {"message": "If this email is registered, a reset link has been sent.", "dev_token": token}
    return {"message": "If this email is registered, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Validate reset token and update the user's password."""
    entry = _reset_tokens.get(req.token)
    if not entry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if datetime.datetime.utcnow() > entry["expires"]:
        _reset_tokens.pop(req.token, None)
        raise HTTPException(status_code=400, detail="Reset token has expired")
    if len(req.new_password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    db = get_db()
    from bson.objectid import ObjectId
    await db.users.update_one(
        {"_id": ObjectId(entry["user_id"])},
        {"$set": {"password": hash_password(req.new_password), "updatedAt": datetime.datetime.utcnow()}}
    )
    _reset_tokens.pop(req.token, None)
    return {"message": "Password updated successfully"}


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Allow authenticated users to change their own password."""
    db = get_db()
    from bson.objectid import ObjectId
    user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(req.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(req.new_password) < 8:
        raise HTTPException(status_code=422, detail="New password must be at least 8 characters")
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"password": hash_password(req.new_password), "updatedAt": datetime.datetime.utcnow()}}
    )
    return {"message": "Password changed successfully"}
