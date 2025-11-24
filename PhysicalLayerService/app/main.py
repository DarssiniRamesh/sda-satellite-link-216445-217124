import os
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

SERVICE_NAME = "PhysicalLayerService"
DEFAULT_PORT = 3000

# Create the FastAPI app with metadata for OpenAPI docs
app = FastAPI(
    title=f"{SERVICE_NAME} API",
    description="FastAPI service scaffolding for the Physical Layer Service (PAT, laser control, modulation, telemetry).",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Health and liveness checks"},
        {"name": "meta", "description": "Informational endpoints"},
    ],
)

# Enable permissive CORS for now (can be tightened later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", tags=["meta"], summary="Root info", description="Returns basic service identifier and status.")
def root() -> Dict[str, Any]:
    """Root endpoint returning service name and status."""
    return {"name": SERVICE_NAME, "status": "running"}

# PUBLIC_INTERFACE
@app.get("/health", tags=["health"], summary="Health check", description="Simple health check returning {'status': 'ok'}.")
def health() -> Dict[str, str]:
    """Health endpoint used by orchestrators and monitoring."""
    return {"status": "ok"}

# PUBLIC_INTERFACE
@app.get("/info", tags=["meta"], summary="Service metadata", description="Returns container metadata and runtime configuration hints.")
def info() -> Dict[str, Any]:
    """Informational endpoint exposing basic metadata for the container."""
    port = int(os.getenv("PORT", DEFAULT_PORT))
    return {
        "service": SERVICE_NAME,
        "version": "0.1.0",
        "description": "Physical Layer Service scaffolding",
        "host": "0.0.0.0",
        "defaultPort": DEFAULT_PORT,
        "effectivePort": port,
        "env": {
            "PORT": os.getenv("PORT"),
        },
    }


def _get_listen_host_port() -> tuple[str, int]:
    """Internal helper to determine bind host and port with env override."""
    host = "0.0.0.0"
    try:
        port = int(os.getenv("PORT", DEFAULT_PORT))
    except (ValueError, TypeError):
        port = DEFAULT_PORT
    return host, port


# Allow running via: python -m app.main or python app/main.py
if __name__ == "__main__":
    # Lazy import to avoid uvicorn being required just to import app in other contexts.
    import uvicorn  # type: ignore

    host, port = _get_listen_host_port()
    uvicorn.run("app.main:app", host=host, port=port, reload=False, workers=1)
