"""
Root-level uvicorn entrypoint shim for preview/CI runners that expect `main:app`.

This imports the FastAPI application object from the PhysicalLayerService package so that
running `uvicorn main:app --host 0.0.0.0 --port 3000` at the repo root works without
activating a virtualenv or adjusting PYTHONPATH.
"""

# PUBLIC_INTERFACE
def get_app():
    """Return the FastAPI app instance from PhysicalLayerService.app.main."""
    from PhysicalLayerService.app.main import app
    return app

# PUBLIC_INTERFACE
# Expose FastAPI app as `app` for uvicorn
app = get_app()

if __name__ == "__main__":
    # Allow running directly as `python main.py` from repo root
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False, workers=1)
