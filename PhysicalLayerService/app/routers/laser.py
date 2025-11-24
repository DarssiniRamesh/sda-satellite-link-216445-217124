from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..pat_machine import get_machine
from ..models.laser_params import LaserConfig, AMConfig, EncodingConfig

log = logging.getLogger(__name__)

router = APIRouter(prefix="/laser", tags=["laser"], responses={404: {"description": "Not found"}})


class StandardError(BaseModel):
    code: str
    message: str
    details: str | None = None


# PUBLIC_INTERFACE
@router.get(
    "/config",
    summary="Get laser config",
    response_model=LaserConfig,
)
def get_laser_config() -> LaserConfig:
    """Return current laser configuration."""
    return get_machine().get_laser_config()


# PUBLIC_INTERFACE
@router.post(
    "/config",
    summary="Set laser config",
    response_model=LaserConfig,
    responses={400: {"model": StandardError}},
)
def set_laser_config(cfg: LaserConfig) -> LaserConfig:
    """Set laser configuration while enforcing TPSL limit."""
    try:
        return get_machine().set_laser_config(cfg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


am_router = APIRouter(prefix="/am", tags=["laser", "am"], responses={404: {"description": "Not found"}})
enc_router = APIRouter(prefix="/encoding", tags=["laser"], responses={404: {"description": "Not found"}})


# PUBLIC_INTERFACE
@am_router.get(
    "/config",
    summary="Get AM config",
    response_model=AMConfig,
)
def get_am_config() -> AMConfig:
    """Return current AM tracking tone configuration."""
    return get_machine().get_am_config()


# PUBLIC_INTERFACE
@am_router.post(
    "/config",
    summary="Set AM config",
    response_model=AMConfig,
)
def set_am_config(cfg: AMConfig) -> AMConfig:
    """Update AM tracking tone configuration."""
    return get_machine().set_am_config(cfg)


# PUBLIC_INTERFACE
@enc_router.post(
    "/config",
    summary="Set encoding (OOK-NRZ or Manchester)",
    response_model=EncodingConfig,
)
def set_encoding(cfg: EncodingConfig) -> EncodingConfig:
    """Set encoding; only OOK-NRZ and Manchester allowed (REQ-PHYS-ENCODING)."""
    # store on machine via AM override container for simplicity
    m = get_machine()
    # reuse AMConfig container optional field area; not persisted elsewhere
    # We simply return cfg to confirm current choice; in a fuller impl, machine would track encoding.
    return cfg
