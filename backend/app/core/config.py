"""Core configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    APP_NAME: str = "signal-hub-alan-vo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment: development|staging|production")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./signal_hub.db",
        description="Database connection URL",
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins",
    )

    # Keycloak / OIDC
    KEYCLOAK_URL: str = Field(default="http://localhost:8080", description="Keycloak base URL")
    KEYCLOAK_REALM: str = Field(default="signal-hub", description="Keycloak realm")
    KEYCLOAK_CLIENT_ID: str = Field(default="signal-hub-backend", description="Keycloak client ID")
    KEYCLOAK_CLIENT_SECRET: str = Field(default="", description="Keycloak client secret")

    # LLM (optional, opt-in)
    LLM_API_KEY: str = Field(default="", description="LLM API key (server-side only)")
    LLM_PROVIDER: str = Field(default="openai-compatible", description="LLM provider")
    LLM_MODEL: str = Field(default="", description="LLM model name")
    LLM_BASE_URL: str = Field(default="", description="LLM base URL override")

    # Sandbox execution
    SANDBOX_TIMEOUT: int = Field(default=30, description="Sandbox execution timeout (seconds)")
    SANDBOX_MEMORY_LIMIT: str = Field(default="256m", description="Sandbox memory limit")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()