from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.security import decode_jwt
from app.db.models import SessionToken, User
from app.db.session import get_db

security = HTTPBearer(auto_error=False)
settings = get_settings()


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    payload = decode_jwt(creds.credentials, settings.jwt_access_secret)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    session = await db.scalar(select(SessionToken).where(SessionToken.token_jti == payload["jti"], SessionToken.revoked.is_(False)))
    if not session:
        raise HTTPException(status_code=401, detail="Session revoked")

    user = await db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
