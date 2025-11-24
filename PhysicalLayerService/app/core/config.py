import functools
import os
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with sensible defaults.
    """

    # Service metadata
    APP_NAME: str = Field("PhysicalLayerService", description="Service name")
    APP_VERSION: str = Field("0.1.0", description="Semantic version of the service")

    # Server settings
    PORT: int = Field(3000, description="Port to bind the service")
    HOST: str = Field("0.0.0.0", description="Host to bind the service")
    RELOAD: bool = Field(False, description="Enable uvicorn reload (dev only)")
    WORKERS: int = Field(1, description="Number of uvicorn workers")

    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("PORT", pre=True)
    def _coerce_port(cls, v):  # type: ignore
        # Allow PORT to be set as string in env
        try:
            return int(v)
        except Exception:
            return 3000


@functools.lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()
