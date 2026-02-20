from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Military Leaders Tool API"
    env: str = Field(default="dev", alias="ENV")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    database_url: str = Field(default="sqlite+aiosqlite:///./mlt.db", alias="DATABASE_URL")

    jwt_access_secret: str = Field(default="change-me-access", alias="JWT_ACCESS_SECRET")
    jwt_refresh_secret: str = Field(default="change-me-refresh", alias="JWT_REFRESH_SECRET")
    jwt_access_ttl_minutes: int = Field(default=15, alias="JWT_ACCESS_TTL_MINUTES")
    jwt_refresh_ttl_minutes: int = Field(default=60 * 24 * 7, alias="JWT_REFRESH_TTL_MINUTES")

    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

    smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")

    owner_email: str = Field(default="", alias="BOOTSTRAP_OWNER_EMAIL")
    owner_password: str = Field(default="", alias="BOOTSTRAP_OWNER_PASSWORD")
    admin_email: str = Field(default="", alias="BOOTSTRAP_ADMIN_EMAIL")
    admin_password: str = Field(default="", alias="BOOTSTRAP_ADMIN_PASSWORD")
    user_email: str = Field(default="", alias="BOOTSTRAP_USER_EMAIL")
    user_password: str = Field(default="", alias="BOOTSTRAP_USER_PASSWORD")

    allow_admin_bypass_2fa: bool = Field(default=False, alias="ALLOW_ADMIN_BYPASS_2FA")


@lru_cache
def get_settings() -> Settings:
    return Settings()
