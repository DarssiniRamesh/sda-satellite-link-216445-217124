from __future__ import annotations

import logging
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..pat_machine import get_machine
from ..models.pat_state import PATStateMachineConfig, PATStatus

log = logging.getLogger(__name__)

router = APIRouter(prefix="/pat", tags=["pat"], responses={404: {"description": "Not found"}})


class StandardError(BaseModel):
    code: str
    message: str
    details: str | None = None


# PUBLIC_INTERFACE
@router.post(
    "/initiate",
    summary="Initiate PAT process",
    response_model=PATStatus,
    responses={400: {"model": StandardError}},
)
def initiate_pat(cfg: PATStateMachineConfig) -> PATStatus:
    """Initiate the PAT process with the provided configuration.

    Parameters:
        cfg: PATStateMachineConfig payload describing acquisition settings.

    Returns:
        PATStatus: Current status after initiation.
    """
    try:
        status = get_machine().initiate(cfg)
        return status
    except ValueError as e:
        log.warning("Failed to initiate PAT: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # pragma: no cover - defensive
        log.exception("Unexpected error initiating PAT")
        raise HTTPException(status_code=500, detail="Internal error") from e


# PUBLIC_INTERFACE
@router.post(
    "/stop",
    summary="Stop PAT process",
    response_model=PATStatus,
    responses={400: {"model": StandardError}},
)
def stop_pat() -> PATStatus:
    """Stop the PAT process and transition to standby."""
    try:
        return get_machine().stop()
    except Exception as e:  # pragma: no cover
        log.exception("Failed to stop PAT")
        raise HTTPException(status_code=500, detail="Internal error") from e


# PUBLIC_INTERFACE
@router.get(
    "/status",
    summary="Get PAT status and telemetry",
    response_model=PATStatus,
)
def get_status() -> PATStatus:
    """Retrieve current PAT status and telemetry snapshot."""
    return get_machine().status()
