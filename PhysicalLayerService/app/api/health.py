from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Returns service health status and timestamp.",
    response_model=dict,
    tags=["health"],
)
# PUBLIC_INTERFACE
def health() -> Dict[str, Any]:
    """Health check endpoint. Returns 200 with basic status."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": "PhysicalLayerService",
        "time": datetime.now(timezone.utc).isoformat(),
        "version": settings.APP_VERSION,
    }
