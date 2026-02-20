import os
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

os.environ["ENV"] = "dev"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_ACCESS_SECRET"] = "test-access"
os.environ["JWT_REFRESH_SECRET"] = "test-refresh"
os.environ["ALLOW_ADMIN_BYPASS_2FA"] = "true"
os.environ["BOOTSTRAP_ADMIN_EMAIL"] = "admin@example.com"
os.environ["BOOTSTRAP_ADMIN_PASSWORD"] = "securepassword1"

from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def cleanup_db():
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass
    yield
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass


@pytest.fixture
async def client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
