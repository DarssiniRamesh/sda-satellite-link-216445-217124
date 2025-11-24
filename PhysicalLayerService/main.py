"""
Compatibility entry module for environments that attempt to import `main:app`.

This module imports and re-exports the FastAPI application from app.main,
ensuring that both `uvicorn app.main:app` (preferred) and `uvicorn main:app`
work for startup in various orchestrators.

Note: The authoritative application and routes are defined in app/main.py.
"""

from typing import Any

# PUBLIC_INTERFACE
def get_app() -> Any:
    """Return the FastAPI app from the canonical module app.main."""
    from app.main import app as _app
    return _app


# Re-export for uvicorn to discover as `main:app`
from app.main import app  # noqa: E402  (import after function definition for clarity)

__all__ = ["app", "get_app"]
