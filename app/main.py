from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.bootstrap import ensure_bootstrap_users
from app.core.config import get_settings
from app.core.middleware import CorrelationIdMiddleware, SecurityHeadersMiddleware
from app.db.models import Base
from app.db.session import AsyncSessionLocal, engine
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.org.router import router as org_router
from app.modules.personnel.router import router as personnel_router
from app.modules.settings.router import router as settings_router
from app.modules.settings.service import SettingsService

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await ensure_bootstrap_users(db)
        await SettingsService.seed_defaults(db)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/ready")
async def ready():
    return {"ok": True, "service": settings.app_name}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(settings_router, prefix=settings.api_prefix)
app.include_router(audit_router, prefix=settings.api_prefix)
app.include_router(personnel_router, prefix=settings.api_prefix)
app.include_router(org_router, prefix=settings.api_prefix)
