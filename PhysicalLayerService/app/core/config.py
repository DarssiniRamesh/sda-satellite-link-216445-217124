import functools
import logging
import os
from typing import List, Any, Dict

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Attempt to import BaseSettings from pydantic-settings (v2)
# If unavailable, provide a minimal shim using BaseModel that reads from os.environ
try:
    from pydantic_settings import BaseSettings  # type: ignore
    _SETTINGS_BACKEND = "pydantic-settings"
except Exception as exc:
    _SETTINGS_BACKEND = "shim"
    logger.error(
        "pydantic-settings is not installed or failed to import (%s). "
        "Proceeding with a minimal shim. "
        "To install, ensure requirements include 'pydantic-settings>=2,<3' and run: pip install -r requirements.txt",
        exc,
    )

    class BaseSettings(BaseModel):  # type: ignore
        """
        Minimal shim for environments missing pydantic-settings.

        This shim:
        - Provides a .model_config attribute compatible with Pydantic v2 config usage.
        - On instantiation, overlays fields with values from environment variables (case-insensitive),
          performing simple type coercion similar to BaseSettings for common types.
        - Ignores unknown env vars.
        NOTE: This is a best-effort fallback to avoid startup crashes in preview/CI environments.
        """

        # Default config mirror; not functionally used but kept for compatibility
        model_config: Dict[str, Any] = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",
        }

        def __init__(self, **data: Any) -> None:
            values = dict(data)
            # Overlay with environment values
            for field_name, field_info in self.model_fields.items():  # type: ignore[attr-defined]
                env_key = field_name
                # Try exact match; if not found and case-insensitive, try uppercase
                env_val = os.getenv(env_key)
                if env_val is None:
                    env_val = os.getenv(env_key.upper())
                if env_val is None:
                    continue

                # Basic coercion for common types
                annotation = field_info.annotation
                try:
                    if annotation in (int,):
                        values[field_name] = int(env_val)
                    elif annotation in (bool,):
                        values[field_name] = env_val.lower() in ("1", "true", "yes", "on")
                    elif annotation in (float,):
                        values[field_name] = float(env_val)
                    elif annotation in (list, List[str]):  # naive comma-separated list
                        values[field_name] = [x.strip() for x in env_val.split(",") if x.strip()]
                    else:
                        values[field_name] = env_val
                except Exception:
                    # On failure, keep default
                    pass
            super().__init__(**values)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with sensible defaults.
    Uses pydantic-settings for Pydantic v2 compatibility when available, otherwise a minimal shim.
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
    Returns a cached Settings instance. Logs which settings backend is used.
    """
    if _SETTINGS_BACKEND != "pydantic-settings":
        logger.warning(
            "Using settings shim backend instead of pydantic-settings. "
            "For full functionality, install 'pydantic-settings>=2,<3'."
        )
    return Settings()
