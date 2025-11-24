from typing import Dict

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get(
    "/version",
    summary="Service version",
    description="Returns service name and semantic version string.",
    response_model=dict,
    tags=["meta"],
)
# PUBLIC_INTERFACE
def version() -> Dict[str, str]:
    """Return service version metadata."""
    settings = get_settings()
    return {"service": "PhysicalLayerService", "version": settings.APP_VERSION}
