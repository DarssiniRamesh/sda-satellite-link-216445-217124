import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.api import health, version

# Configure logging before anything else
configure_logging()

logger = logging.getLogger(__name__)

# Lifespan context for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    logger.info("PhysicalLayerService starting up")
    try:
        yield
    finally:
        logger.info("PhysicalLayerService shutting down")


def create_app() -> FastAPI:
    """
    Factory to create FastAPI app with routers, settings, CORS, and docs metadata.
    """
    settings: Settings = get_settings()

    app = FastAPI(
        title="PhysicalLayerService",
        description="Physical Layer Service for SDA Satellite Link - PAT control, laser control, modulation, and safety.",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        openapi_tags=[
            {"name": "health", "description": "Service health and diagnostics"},
            {"name": "meta", "description": "Service metadata and version"},
        ],
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="", tags=["health"])
    app.include_router(version.router, prefix="", tags=["meta"])

    @app.get(
        "/",
        tags=["meta"],
        summary="Root docs",
        description="Root endpoint with basic service information.",
        response_model=Dict[str, str],
    )
    # PUBLIC_INTERFACE
    def root() -> Dict[str, str]:
        """Returns a basic message and links."""
        return {
            "service": "PhysicalLayerService",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "version": "/version",
        }

    return app


app = create_app()

if __name__ == "__main__":
    # Allow running via: python -m app.main
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
    )
