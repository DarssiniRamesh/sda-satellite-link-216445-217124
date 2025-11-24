"""
Thin entrypoint module for ASGI servers.

This file exists to support orchestrators that start the service using:
    uvicorn main:app

It re-exports the FastAPI `app` object defined in src.api.main without
binding to any specific host or port, leaving that to the process manager
or environment. This keeps configuration centralized in src.api.main.
"""

from __future__ import annotations

# PUBLIC_INTERFACE
def get_app():
    """Return the FastAPI app instance from src.api.main.

    This provides an explicit function that can be used by tooling that prefers
    a callable factory pattern. For uvicorn main:app, the module-level `app`
    is also exported below.
    """
    # Import locally to avoid side effects at module import time if desired.
    # This is safe here since src.api.main performs only app construction and
    # logging configuration without performing external I/O.
    from src.api.main import app  # type: ignore

    return app


# Expose `app` at module-level for uvicorn discoverability (uvicorn main:app)
app = get_app()
