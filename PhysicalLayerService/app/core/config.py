import functools
import logging
import os
from typing import List, Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Robust import strategy: prefer pydantic-settings; if unavailable, fall back to local shim.
_SETTINGS_BACKEND: str = "pydantic-settings"
try:
    from pydantic_settings import BaseSettings  # type: ignore
except Exception as exc:
    # Fallback to shim that emulates BaseSettings enough for our needs.
    _SETTINGS_BACKEND = "shim"
    logger.warning(
        "pydantic-settings not available (%s). Using minimal BaseSettings shim. "
        "Install 'pydantic-settings>=2,<3' for full functionality.",
        exc,
    )

    class BaseSettings(BaseModel):  # type: ignore
        """
        Minimal shim for environments missing pydantic-settings.

        Behavior:
        - Provides a model_config attribute compatible with common Pydantic v2 settings patterns.
        - On instantiation, overlays model fields with values from environment variables (case-insensitive).
        - Simple type coercion for int, bool, float, and basic comma-separated lists.
        - Silently ignores conversion errors to avoid startup failure.
        """

        # Default config semantics (best-effort)
        model_config: Dict[str, Any] = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",
        }

        def __init__(self, **data: Any) -> None:
            values = dict(data)
            # Overlay with environment values
            model_fields = getattr(self, "model_fields", None)  # type: ignore[attr-defined]
            if not model_fields and hasattr(type(self), "model_fields"):
                model_fields = getattr(type(self), "model_fields")  # type: ignore[attr-defined]
            for field_name, field_info in (model_fields or {}).items():  # type: ignore[union-attr]
                env_key = field_name
                # Try exact match then uppercase
                env_val: Optional[str] = os.getenv(env_key)
                if env_val is None:
                    env_val = os.getenv(env_key.upper())
                if env_val is None:
                    continue

                # Basic coercion for common types
                annotation = getattr(field_info, "annotation", None)
                try:
                    if annotation in (int,):
                        values[field_name] = int(env_val)
                    elif annotation in (bool,):
                        values[field_name] = env_val.strip().lower() in ("1", "true", "yes", "on")
                    elif annotation in (float,):
                        values[field_name] = float(env_val)
                    elif annotation in (list, List[str]):  # naive comma-separated list
                        values[field_name] = [x.strip() for x in env_val.split(",") if x.strip()]
                    else:
                        values[field_name] = env_val
                except Exception:
                    # Keep provided default if coercion fails
                    pass
            super().__init__(**values)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with sensible defaults.
    Uses pydantic-settings when available, otherwise a minimal shim to avoid crashes.
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

    # Pydantic v2 config
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
    Returns a cached Settings instance. Logs which settings backend is used.
    """
    if _SETTINGS_BACKEND != "pydantic-settings":
        logger.warning(
            "Using settings shim backend instead of pydantic-settings. "
            "For full functionality, install 'pydantic-settings>=2,<3'."
        )
    return Settings()
