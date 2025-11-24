from __future__ import annotations

import enum
import time
from datetime import datetime, timezone
from typing import Optional, Literal

from pydantic import BaseModel, Field, validator


class PATState(str, enum.Enum):
    STANDBY = "standby"
    SETUP = "setup"
    COARSE_ACQ = "coarse_acq"
    FINE_ACQ = "fine_acq"
    COMMUNICATION = "communication"
    STOP = "stop"
    PREPARE = "prepare"


class LinkQuality(BaseModel):
    """Represents link quality metrics exposed in telemetry."""
    BLER: float = Field(0.0, description="Block Error Rate [0..1]")
    RSSI: float = Field(0.0, description="Received Signal Strength Indicator [dBm or relative]")
    syncStatus: Literal["unsynced", "acquiring", "locked"] = Field(
        "unsynced", description="Synchronization status"
    )

    @validator("BLER")
    def _validate_bler(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("BLER must be in [0,1]")
        return float(v)


class Telemetry(BaseModel):
    """Minimal telemetry record for streaming/state reporting."""
    state: PATState = Field(..., description="Current PAT state")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp from host clock",
    )
    linkQuality: LinkQuality = Field(default_factory=LinkQuality, description="Link quality metrics")


class PATStatus(BaseModel):
    """PAT status payload for /pat/status"""
    state: PATState = Field(..., description="Current state")
    entryTime: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time the machine entered the current state",
    )
    telemetry: Telemetry = Field(default_factory=Telemetry, description="Embedded telemetry snapshot")


class PATStateMachineConfig(BaseModel):
    """Configuration for initiating PAT."""
    leadOrFollow: Literal["lead", "follow"] = Field(..., description="Role for acquisition choreography")
    uncertaintyCone: float = Field(..., ge=0.0, description="Pointing uncertainty (deg)")
    phase1ADuration: int = Field(..., ge=0, description="Phase 1A duration (s)")
    phase1BDuration: int = Field(..., ge=0, description="Phase 1B duration (s)")
    spiralVelocity: float = Field(..., ge=0.0, description="Spiral scan angular velocity (deg/s)")
    spiralSeparation: float = Field(..., ge=0.0, description="Spiral arm separation (deg)")
    txWavelength: Literal["-1", "20"] = Field(
        "20",
        description="Channel slot code placeholder aligned with ITU-T G.694 mapping (-1 reserved, 20 nominal)"
    )
    trackingTone: bool = Field(True, description="Enable AM tracking tone")
    trackingToneFrequency: Literal[40, 50] = Field(40, description="AM tracking tone frequency (kHz)")
    modulationIndex: float = Field(0.2, description="AM modulation index [0..1]")
    acquisitionPeriod: int = Field(60, ge=1, le=100, description="Overall acquisition target duration (s)")

    @validator("modulationIndex")
    def _validate_mi(cls, v: float) -> float:
        if not (0.0 <= v <= 0.8):
            # bound to max 0.8 per request enumerations
            raise ValueError("modulationIndex must be between 0.0 and 0.8")
        return float(v)

    @validator("trackingToneFrequency")
    def _validate_tone(cls, v: int) -> int:
        if v not in (40, 50):
            raise ValueError("trackingToneFrequency must be 40 or 50 (kHz)")
        return v


class PATRuntimeState(BaseModel):
    """Internal runtime state for the PAT state machine."""
    state: PATState = PATState.STANDBY
    entry_time_monotonic: float = Field(default_factory=time.monotonic)
    entry_time_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config: Optional[PATStateMachineConfig] = None

    def as_status(self) -> PATStatus:
        return PATStatus(state=self.state, entryTime=self.entry_time_utc, telemetry=Telemetry(state=self.state))
