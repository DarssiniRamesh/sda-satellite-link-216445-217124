from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .settings import get_settings, Settings

# Configure module-level logger compatible with uvicorn's logging.
logger = logging.getLogger("uvicorn.error")


class HealthResponse(BaseModel):
    """Response model for health endpoint."""

    status: str = Field(..., description="Overall health status of the service")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class RootResponse(BaseModel):
    """Response model for root endpoint with basic metadata."""

    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Short description of the service")
    docs_url: str = Field(..., description="URL for interactive API docs")
    openapi_url: str = Field(..., description="URL for the OpenAPI specification")


def _create_app(settings: Settings) -> FastAPI:
    """
    Internal application factory to allow dependency-injection-friendly patterns.

    This keeps configuration centralized and testable.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        openapi_tags=[
            {"name": "health", "description": "Health and diagnostics"},
            {"name": "meta", "description": "Service metadata"},
        ],
    )

    # Basic CORS configuration; restrict in production via env.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    # Root metadata endpoint
    # PUBLIC_INTERFACE
    @app.get(
        "/",
        response_model=RootResponse,
        tags=["meta"],
        summary="Service metadata",
        description="Returns basic metadata about the service, including version and docs links.",
    )
    def read_root() -> RootResponse:
        """Root endpoint returning minimal service metadata."""
        return RootResponse(
            name=settings.APP_NAME,
            version=settings.APP_VERSION,
            description=settings.APP_DESCRIPTION,
            docs_url=str(app.docs_url or ""),
            openapi_url=str(app.openapi_url or ""),
        )

    # Health endpoint
    # PUBLIC_INTERFACE
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["health"],
        summary="Health check",
        description="Returns healthy if the service is up and able to respond.",
    )
    def health() -> HealthResponse:
        """Health endpoint used for container orchestration probes."""
        return HealthResponse(
            status="healthy", service=settings.APP_NAME, version=settings.APP_VERSION
        )

    @app.on_event("startup")
    async def on_startup() -> None:
        """Log startup with sanitized configuration details."""
        try:
            logger.info(
                "Starting %s v%s",
                settings.APP_NAME,
                settings.APP_VERSION,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Startup logging failed: %s", exc)

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        """Log clean shutdown."""
        try:
            logger.info("Shutting down %s", settings.APP_NAME)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Shutdown logging failed: %s", exc)

    return app


# Settings are read once at import, but values are from environment without hardcoding.
_settings = get_settings()
app = _create_app(_settings)
