from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


CBAND_MIN_NM = 1530.0
CBAND_MAX_NM = 1565.0
CHANNEL_SPACING_GHZ = 100.0

ALLOWED_MI = {0.0, 0.1, 0.2, 0.33, 0.8}


def _is_valid_cband_nm(wavelength_nm: float) -> bool:
    return CBAND_MIN_NM <= wavelength_nm <= CBAND_MAX_NM


class LaserConfig(BaseModel):
    """Laser configuration surface for GET/POST /laser/config."""
    # For simplicity, align with spec placeholder mapping strings "-1" or "20" for channel code.
    wavelength: Literal["-1", "20"] = Field(
        "20", description="ITU-T G.694 grid slot encoding (placeholder)."
    )
    power: float = Field(0.5, ge=0.0, le=2.5, description="Output optical power (W)")
    modulationIndex: float = Field(0.2, description="AM modulation index [0..1, bounded to enumerated set]")

    @validator("modulationIndex")
    def _validate_mi(cls, v: float) -> float:
        if v not in ALLOWED_MI:
            raise ValueError(f"modulationIndex must be one of {sorted(ALLOWED_MI)}")
        return float(v)


class AMConfig(BaseModel):
    """Amplitude modulation tracking tone configuration."""
    enabled: bool = Field(True, description="Enable/disable tracking tone")
    frequency: Literal[40, 50] = Field(40, description="Tracking tone frequency (kHz)")
    modulationIndex: float = Field(0.2, description="AM modulation index [bounded list]")

    @validator("modulationIndex")
    def _validate_mi(cls, v: float) -> float:
        if v not in ALLOWED_MI:
            raise ValueError(f"modulationIndex must be one of {sorted(ALLOWED_MI)}")
        return float(v)


class TPSLConfig(BaseModel):
    """Transmitted Power Safety Limit configuration for /power/tpsl."""
    limit: float = Field(2.5, ge=0.0, description="Max transmit power (W)")
    enforced: bool = Field(True, description="Whether to enforce the limit")


class EncodingConfig(BaseModel):
    """Encoding configuration to select OOK-NRZ or Manchester."""
    encoding: Literal["OOK-NRZ", "Manchester"] = Field(
        "OOK-NRZ", description="Encoding selection for payload signaling."
    )
    # Placeholder for future parameters if needed
    am: Optional[AMConfig] = Field(default=None, description="Optional AM override")
