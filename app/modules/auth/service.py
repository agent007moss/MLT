from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.security import (
    constant_time_eq,
    decode_jwt,
    generate_otp,
    hash_password,
    hash_value,
    make_jwt,
    verify_password,
)
from app.db.models import OTPChallenge, SessionToken, User
from app.modules.audit.service import AuditService

settings = get_settings()


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, email: str, username: str, password: str) -> User:
        exists = await db.scalar(select(User).where((User.email == email) | (User.username == username)))
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        user = User(email=email, username=username, password_hash=hash_password(password), role="USER")
        db.add(user)
        await AuditService.add_event(db, None, "auth.register", "user", {"email": email})
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def verify_email(db: AsyncSession, email: str) -> bool:
        user = await db.scalar(select(User).where(User.email == email))
        if not user:
            return False
        user.is_email_verified = True
        await AuditService.add_event(db, user.id, "auth.verify_email", "user", {"email": email})
        await db.commit()
        return True

    @staticmethod
    async def login_start(db: AsyncSession, username_or_email: str, password: str) -> dict:
        user = await db.scalar(select(User).where((User.email == username_or_email) | (User.username == username_or_email)))
        if not user or not verify_password(password, user.password_hash):
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Account temporarily locked")

        if settings.allow_admin_bypass_2fa and user.role in {"OWNER", "ADMIN"} and settings.env != "prod":
            tokens = await AuthService._issue_tokens(db, user)
            await AuditService.add_event(db, user.id, "auth.admin_bypass_2fa", "session", {})
            await db.commit()
            return {"mode": "tokens", **tokens}

        existing = await db.scalar(
            select(OTPChallenge).where(and_(OTPChallenge.user_id == user.id, OTPChallenge.status == "PENDING"))
        )
        if existing:
            existing.status = "SUPERSEDED"

        code = generate_otp()
        challenge = OTPChallenge(
            user_id=user.id,
            code_hash=hash_value(code),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            retries=0,
            status="PENDING",
        )
        db.add(challenge)
        await AuditService.add_event(db, user.id, "auth.login_otp_challenge", "session", {"otp_mock": code})
        await db.commit()
        response = {"mode": "otp_required", "message": "OTP sent via email"}
        if settings.env != "prod":
            response["debug_otp"] = code
        return response

    @staticmethod
    async def verify_otp(db: AsyncSession, username_or_email: str, code: str) -> dict:
        user = await db.scalar(select(User).where((User.email == username_or_email) | (User.username == username_or_email)))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid challenge")

        challenge = await db.scalar(
            select(OTPChallenge).where(and_(OTPChallenge.user_id == user.id, OTPChallenge.status == "PENDING"))
        )
        if not challenge or challenge.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="OTP expired or missing")
        if challenge.retries >= 5:
            raise HTTPException(status_code=423, detail="OTP retry limit reached")

        if not constant_time_eq(challenge.code_hash, hash_value(code)):
            challenge.retries += 1
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid OTP")

        challenge.status = "VERIFIED"
        user.failed_login_attempts = 0
        user.locked_until = None
        tokens = await AuthService._issue_tokens(db, user)
        await AuditService.add_event(db, user.id, "auth.verify_2fa", "session", {})
        await db.commit()
        return tokens

    @staticmethod
    async def _issue_tokens(db: AsyncSession, user: User) -> dict:
        access_token, access_jti, _ = make_jwt(
            subject=str(user.id),
            token_type="access",
            ttl_minutes=settings.jwt_access_ttl_minutes,
            secret=settings.jwt_access_secret,
            extra={"role": user.role},
        )
        refresh_token, refresh_jti, refresh_exp = make_jwt(
            subject=str(user.id),
            token_type="refresh",
            ttl_minutes=settings.jwt_refresh_ttl_minutes,
            secret=settings.jwt_refresh_secret,
        )
        db.add(SessionToken(user_id=user.id, token_jti=access_jti, refresh_jti=refresh_jti, expires_at=refresh_exp))
        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    async def refresh(db: AsyncSession, refresh_token: str) -> dict:
        payload = decode_jwt(refresh_token, settings.jwt_refresh_secret)
        session = await db.scalar(select(SessionToken).where(SessionToken.refresh_jti == payload["jti"], SessionToken.revoked.is_(False)))
        if not session:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        session.revoked = True
        user = await db.get(User, int(payload["sub"]))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        tokens = await AuthService._issue_tokens(db, user)
        await AuditService.add_event(db, user.id, "auth.refresh", "session", {})
        await db.commit()
        return tokens

    @staticmethod
    async def logout(db: AsyncSession, user_id: int) -> None:
        sessions = (await db.execute(select(SessionToken).where(SessionToken.user_id == user_id, SessionToken.revoked.is_(False)))).scalars().all()
        for s in sessions:
            s.revoked = True
        await AuditService.add_event(db, user_id, "auth.logout", "session", {})
        await db.commit()
