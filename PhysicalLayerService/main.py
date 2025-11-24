"""
Local uvicorn entrypoint for running from the PhysicalLayerService directory.

This file ensures `uvicorn main:app` works when executed inside the
sda-satellite-link-216445-217124/PhysicalLayerService folder, while also
remaining compatible when invoked from the repository root.

It implements a dual import strategy:
- First, try to import from the monorepo package path `PhysicalLayerService.app.main`
- Fallback to the local package path `app.main`

Usage:
  cd sda-satellite-link-216445-217124/PhysicalLayerService
  uvicorn main:app --host 0.0.0.0 --port 3000

The default PORT should be 3000 if not otherwise specified.
"""

from typing import Any

# PUBLIC_INTERFACE
def get_app() -> Any:
    """Return the FastAPI app instance from the service's app module.
    
    Tries importing from both repository root and local container contexts.
    """
    try:
        # When running from repo root where 'PhysicalLayerService' is a top-level package
        from PhysicalLayerService.app.main import app  # type: ignore
        return app
    except Exception:
        # When running from inside the container folder where 'app' is the local package
        from app.main import app  # type: ignore
        return app


# PUBLIC_INTERFACE
# Expose FastAPI app as `app` for uvicorn
app = get_app()

if __name__ == "__main__":
    # Allow running directly as `python main.py` from the container folder
    import uvicorn
    # Default to PORT=3000 if env/config not available
    try:
        from app.core.config import get_settings
        settings = get_settings()
        port = int(getattr(settings, "PORT", 3000) or 3000)
        host = getattr(settings, "HOST", "0.0.0.0") or "0.0.0.0"
        reload = bool(getattr(settings, "RELOAD", False))
        workers = int(getattr(settings, "WORKERS", 1) or 1)
    except Exception:
        host = "0.0.0.0"
        port = 3000
        reload = False
        workers = 1

    uvicorn.run("main:app", host=host, port=port, reload=reload, workers=workers)
