import logging
import os
from typing import Optional

import uvicorn

# Import the FastAPI app from main
from .main import app  # noqa: F401

logger = logging.getLogger("uvicorn.error")
logging.basicConfig(level=logging.INFO)


def _get_allowed_port(env_port: Optional[str]) -> int:
    """
    Internal helper to determine the port to use from the environment,
    constrained to the allowed set to avoid conflicts.
    """
    allowed_ports = {3000, 3001, 3002, 5000}
    default_port = 5000
    if not env_port:
        return default_port
    try:
        port_val = int(env_port)
    except ValueError:
        logger.warning("Invalid PORT value '%s'. Falling back to default %d.", env_port, default_port)
        return default_port
    if port_val not in allowed_ports:
        logger.warning(
            "PORT %s is not in allowed set %s. Falling back to default %d.",
            port_val,
            sorted(list(allowed_ports)),
            default_port,
        )
        return default_port
    return port_val


# PUBLIC_INTERFACE
def run() -> None:
    """Run the FastAPI application with uvicorn.

    This function reads the PORT environment variable (if provided) and validates it
    against the allowed set {3000, 3001, 3002, 5000}. If invalid or missing, it defaults to 5000.

    The server binds to host 0.0.0.0 to be reachable within containerized environments.

    Environment variables:
    - PORT: Optional. Must be one of 3000, 3001, 3002, 5000. Defaults to 5000.
    """
    port = _get_allowed_port(os.getenv("PORT"))
    logger.info("Starting PhysicalLayerService on 0.0.0.0:%d", port)

    # Use uvicorn to serve the app. We reference the module path to ensure discoverability.
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("UVICORN_RELOAD", "false").lower() == "true",
        workers=int(os.getenv("UVICORN_WORKERS", "1")),
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )
    # Note: Swagger UI is enabled by default at /docs and OpenAPI JSON at /openapi.json


if __name__ == "__main__":
    run()
