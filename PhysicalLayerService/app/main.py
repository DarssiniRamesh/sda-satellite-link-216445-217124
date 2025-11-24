import os
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.pat import router as pat_router
from .routers.laser import router as laser_router, am_router as am_cfg_router, enc_router as encoding_router
from .routers.safety import router as safety_router
from .routers.telemetry import router as telemetry_router

SERVICE_NAME = "PhysicalLayerService"
DEFAULT_PORT = 3000

# Create the FastAPI app with metadata for OpenAPI docs
# PUBLIC_INTERFACE
app = FastAPI(
    title=f"{SERVICE_NAME} API",
    description="Physical Layer Service: PAT state machine, laser control, AM tracking tone, telemetry.",
    version="0.2.0",
    openapi_tags=[
        {"name": "health", "description": "Health and liveness checks"},
        {"name": "meta", "description": "Informational endpoints"},
        {"name": "pat", "description": "Pointing, Acquisition, and Tracking control"},
        {"name": "laser", "description": "Laser configuration"},
        {"name": "am", "description": "AM tracking tone configuration (REQ-PHYS-AM-TONE)"},
        {"name": "laser", "description": "Encoding selection (REQ-PHYS-ENCODING)"},
        {"name": "telemetry", "description": "Telemetry retrieval and streaming"},
        {"name": "safety", "description": "Safety limits (TPSL)"},
        {"name": "power", "description": "Power management"},
    ],
    contact={"name": "PhysicalLayerService", "url": "https://example.com"},
    license_info={"name": "Proprietary"},
)

# Enable permissive CORS for now (can be tightened later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(pat_router)
app.include_router(laser_router)
app.include_router(am_cfg_router)
app.include_router(encoding_router)
app.include_router(safety_router)
app.include_router(telemetry_router)


# PUBLIC_INTERFACE
@app.get("/", tags=["meta"], summary="Root info", description="Returns basic service identifier and status.")
def root() -> Dict[str, Any]:
    """Root endpoint returning service name and status.

    Returns:
        dict: A simple object containing service name and status.
    """
    return {"name": SERVICE_NAME, "status": "running"}

# PUBLIC_INTERFACE
@app.get("/health", tags=["health"], summary="Health check", description="Simple health check returning {'status': 'ok'}.")
def health() -> Dict[str, str]:
    """Health endpoint used by orchestrators and monitoring.

    Returns:
        dict: Health status object with 'ok' if service is up.
    """
    return {"status": "ok"}

# PUBLIC_INTERFACE
@app.get("/info", tags=["meta"], summary="Service metadata", description="Returns container metadata and runtime configuration hints.")
def info() -> Dict[str, Any]:
    """Informational endpoint exposing basic metadata for the container.

    Returns:
        dict: Service metadata including effective port and env details.
    """
    port = int(os.getenv("PORT", DEFAULT_PORT))
    return {
        "service": SERVICE_NAME,
        "version": "0.2.0",
        "description": "Physical Layer Service with PAT, laser, telemetry, and safety endpoints",
        "host": "0.0.0.0",
        "defaultPort": DEFAULT_PORT,
        "effectivePort": port,
        "env": {
            "PORT": os.getenv("PORT"),
        },
        "websocketHelp": "/telemetry/ws-help",
    }


# PUBLIC_INTERFACE
@app.get(
    "/telemetry/ws-help",
    tags=["telemetry"],
    summary="WebSocket usage help",
    description="Provides usage notes for the telemetry WebSocket endpoint at /telemetry/ws.",
)
def telemetry_ws_help() -> Dict[str, Any]:
    """Returns documentation for telemetry WebSocket usage."""
    return {
        "endpoint": "/telemetry/ws",
        "operationId": "telemetryWs",
        "summary": "Receive Telemetry frames over WebSocket",
        "notes": [
            "Connect to ws://<host>/telemetry/ws",
            "Server sends JSON Telemetry objects at ~2 Hz (mocked)",
            "Fields: state, timestamp (UTC), linkQuality (BLER, RSSI, syncStatus)",
        ],
        "example": {
            "state": "coarse_acq",
            "timestamp": "2024-01-01T00:00:00Z",
            "linkQuality": {"BLER": 0.02, "RSSI": -67.2, "syncStatus": "acquiring"},
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
