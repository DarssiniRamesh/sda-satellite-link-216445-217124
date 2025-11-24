"""
ASGI entrypoint for PhysicalLayerService.

This file exposes the FastAPI `app` object so that running:
    uvicorn main:app --host 0.0.0.0 --port 3001
from the PhysicalLayerService directory will correctly import the application.

Notes:
- The actual application is defined in src/api/main.py.
- Keep this thin and free of side effects to avoid import-time errors.
"""

# PUBLIC_INTERFACE
from src.api.main import app  # FastAPI instance
"""FastAPI app instance re-exported for uvicorn entrypoint (main:app)."""

# Explicit module export for tooling and linters
__all__ = ["app"]
