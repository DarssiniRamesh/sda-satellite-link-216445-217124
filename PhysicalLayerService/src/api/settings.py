from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application runtime settings loaded from environment variables."""

    APP_NAME: str = Field(default="PhysicalLayerService", description="Service name")
    APP_VERSION: str = Field(default="0.1.0", description="Service version")
    APP_DESCRIPTION: str = Field(
        default=(
            "Implements PAT state machine logic, laser control, tracking tone, "
            "modulations, optical TX/RX, and safety controls."
        ),
        description="Short description for service",
    )
    # The preview system manages ports; PORT is read for metadata only and not bound here.
    PORT: int = Field(default=int(os.getenv("PORT", "8000")), description="Port (metadata only)")

    # Comma-separated origins in env; fallback to '*' for dev convenience.
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
        description="Allowed CORS origins",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    PUBLIC_INTERFACE
    Returns cached Settings instance loaded from environment variables.

    This function should be used wherever configuration is required to avoid
    reading environment repeatedly and to support dependency injection in tests.
    """
    return Settings()
