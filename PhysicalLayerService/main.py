"""
Local uvicorn entrypoint for running from the PhysicalLayerService directory.

This file ensures `uvicorn main:app` works when executed inside the
sda-satellite-link-216445-217124/PhysicalLayerService folder, while also
remaining compatible when invoked from the repository root.

It implements a dual import strategy:
- First, try to import from the monorepo package path `PhysicalLayerService.app.main`
- Fallback to the local package path `app.main`

If import fails due to path context, minimally adjust sys.path to include the
repository root so that `PhysicalLayerService.app.main` becomes importable.

Usage:
  cd sda-satellite-link-216445-217124/PhysicalLayerService
  uvicorn main:app --host 0.0.0.0 --port 3000

The default PORT should be 3000 if not otherwise specified.
"""

from typing import Any
import os
import sys


def _ensure_repo_root_on_sys_path() -> None:
    """
    Add the repository root to sys.path if not already present.

    This avoids hardcoding paths while ensuring that the top-level package
    `PhysicalLayerService` can be imported when running from this folder directly.
    """
    try:
        # Current file: <repo>/sda-satellite-link-216445-217124/PhysicalLayerService/main.py
        this_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(this_dir, os.pardir))  # .. => <repo>/sda-.../
        # Add the parent of that path as well if root-level shim might be needed
        top_root = os.path.abspath(os.path.join(repo_root, os.pardir))
        for candidate in (top_root, repo_root):
            if candidate and candidate not in sys.path:
                sys.path.insert(0, candidate)
    except Exception:
        # Best-effort; if it fails, imports may still work via local package
        pass


# PUBLIC_INTERFACE
def get_app() -> Any:
    """Return the FastAPI app instance from the service's app module.

    Tries importing from both repository root and local container contexts.
    Minimally adjusts sys.path if needed to locate the repo root.
    """
    # First, attempt monorepo-style import
    try:
        from PhysicalLayerService.app.main import app  # type: ignore
        return app
    except Exception:
        # If that failed, try to minimally fix sys.path and retry
        _ensure_repo_root_on_sys_path()
        try:
            from PhysicalLayerService.app.main import app  # type: ignore
            return app
        except Exception:
            # Finally, fallback to local package import
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
