from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..pat_machine import get_machine
from ..models.laser_params import TPSLConfig

router = APIRouter(prefix="/power", tags=["safety", "power"], responses={404: {"description": "Not found"}})


class StandardError(BaseModel):
    code: str
    message: str
    details: str | None = None


# PUBLIC_INTERFACE
@router.get(
    "/tpsl",
    summary="Get TPSL config",
    response_model=TPSLConfig,
)
def get_tpsl() -> TPSLConfig:
    """Return Transmitted Power Safety Limit configuration."""
    return get_machine().get_tpsl()


# PUBLIC_INTERFACE
@router.post(
    "/tpsl",
    summary="Set TPSL config",
    response_model=TPSLConfig,
    responses={400: {"model": StandardError}},
)
def set_tpsl(cfg: TPSLConfig) -> TPSLConfig:
    """Set Transmitted Power Safety Limit configuration."""
    try:
        return get_machine().set_tpsl(cfg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
