"""FastAPI application for the Physical Layer Service (PAT, laser control, telemetry).

This module defines the ASGI app used by uvicorn. It is imported by the top-level
ASGI entrypoint (main.py) and can also be run via `python -m src.api`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# PUBLIC_INTERFACE
app = FastAPI(
    title="Physical Layer Service",
    description="FastAPI application for the Physical Layer Service (PAT, laser control, telemetry).",
    version="0.1.0",
)

# Enable permissive CORS for development/previews; consider restricting in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check() -> dict:
    """Simple health check endpoint.

    Returns:
        dict: A JSON object indicating service health.
    """
    return {"message": "Healthy"}
