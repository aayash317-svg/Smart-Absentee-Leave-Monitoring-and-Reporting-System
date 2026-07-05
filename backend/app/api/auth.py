from fastapi import APIRouter, Depends, status, Body
from ..schemas.auth import UserRegister, UserLogin, Token, UserOut
from ..services.auth_service import AuthService
from .deps import get_current_user

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
