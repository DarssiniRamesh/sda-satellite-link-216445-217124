import functools
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pydantic import Extra


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with sensible defaults.
    Uses pydantic-settings for Pydantic v2 compatibility.
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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # ignore unexpected environment variables
    }

    @field_validator("PORT", mode="before")
    def _coerce_port(cls, v):  # type: ignore
        # Allow PORT to be set as string in env; default to 3000 on failure
        try:
            return int(v)
        except Exception:
            return 3000


@functools.lru_cache()
# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()
