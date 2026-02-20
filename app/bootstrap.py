from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models import User

settings = get_settings()


async def ensure_bootstrap_users(db: AsyncSession):
    seeds = [
        ("OWNER", settings.owner_email, settings.owner_password, "owner"),
        ("ADMIN", settings.admin_email, settings.admin_password, "admin"),
        ("USER", settings.user_email, settings.user_password, "user"),
    ]
    for role, email, password, fallback_username in seeds:
        if not email or not password:
            continue
        exists = await db.scalar(select(User).where(User.email == email))
        if exists:
            continue
        db.add(
            User(
                email=email,
                username=email.split("@")[0] if "@" in email else fallback_username,
                password_hash=hash_password(password),
                is_email_verified=True,
                role=role,
            )
        )
    await db.commit()
