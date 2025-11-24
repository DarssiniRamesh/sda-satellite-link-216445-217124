from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..pat_machine import get_machine
from ..models.pat_state import Telemetry

log = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["telemetry"], responses={404: {"description": "Not found"}})


class StandardError(BaseModel):
    code: str
    message: str
    details: str | None = None


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="Get real-time telemetry snapshot",
    response_model=Telemetry,
)
def get_telemetry() -> Telemetry:
    """Return a snapshot of current telemetry (state, timestamp, link quality)."""
    return get_machine().telemetry()


async def _telemetry_stream() -> AsyncGenerator[Telemetry, None]:
    """Internal generator for telemetry updates (mocked at ~2 Hz)."""
    while True:
        yield get_machine().telemetry()
        await asyncio.sleep(0.5)


# PUBLIC_INTERFACE
@router.websocket(
    "/ws",
)
async def telemetry_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint streaming telemetry.

    Operation:
    - Connect to ws://<host>/telemetry/ws to receive JSON-serialized Telemetry objects.
    - Server sends updates periodically (~2 Hz mocked).
    """
    await websocket.accept()
    try:
        async for t in _telemetry_stream():
            # Serialize via Pydantic for safety
            await websocket.send_text(t.json())
    except WebSocketDisconnect:
        log.info("Telemetry WS disconnected")
    except Exception as e:  # pragma: no cover
        log.exception("Telemetry WS error: %s", e)
        try:
            await websocket.send_text(json.dumps({"error": "internal"}))
        except Exception:
            pass
        finally:
            await websocket.close(code=1011)
