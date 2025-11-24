"""FastAPI application for the Physical Layer Service (PAT, laser control, telemetry).

This module defines the ASGI app used by uvicorn. It is imported by the top-level
ASGI entrypoint (main.py) and can also be run via `python -m src.api`.
"""

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# PUBLIC_INTERFACE
app = FastAPI(
    title="Physical Layer Service",
    description="FastAPI application for the Physical Layer Service (PAT, laser control, telemetry).",
    version="0.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health and liveness checks."},
    ],
)

# Enable permissive CORS for development/previews; consider restricting in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this list to trusted origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check() -> Dict[str, str]:
    """Simple health check endpoint.

    Returns:
        dict: A JSON object indicating service health.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get("/health", tags=["Health"], summary="Readiness/Health probe")
def readiness() -> Dict[str, str]:
    """Explicit readiness/health endpoint for probes and load balancers.

    Returns:
        dict: Health status.
    """
    return {"status": "ok"}
