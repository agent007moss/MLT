from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.deps import get_current_user
from app.modules.auth.schemas import LoginRequest, MeResponse, RefreshRequest, RegisterRequest, TokenPairResponse, Verify2FARequest
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register(db, payload.email, payload.username, payload.password)
    return {"id": user.id, "email": user.email, "username": user.username}


@router.get("/verify-email")
async def verify_email(email: str = Query(...), db: AsyncSession = Depends(get_db)):
    ok = await AuthService.verify_email(db, email)
    return {"verified": ok}


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_start(db, payload.username_or_email, payload.password)


@router.post("/verify-2fa", response_model=TokenPairResponse)
async def verify_2fa(payload: Verify2FARequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.verify_otp(db, payload.username_or_email, payload.code)


@router.post("/logout")
async def logout(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await AuthService.logout(db, current_user.id)
    return {"ok": True}


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.refresh(db, payload.refresh_token)


@router.get("/me", response_model=MeResponse)
async def me(current_user=Depends(get_current_user)):
    return current_user
