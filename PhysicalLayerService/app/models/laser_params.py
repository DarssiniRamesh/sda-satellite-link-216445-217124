from __future__ import annotations

from typing import Literal, Optional, Tuple

from pydantic import BaseModel, Field, validator


# Requirement IDs referenced in validations (examples):
# REQ-OPT-CBAND-100GHZ: C-Band operation 1530–1565 nm with 100 GHz ITU-T G.694 channel spacing
# REQ-PHYS-AM-TONE: AM tracking tone frequency restricted to 40 kHz or 50 kHz
# REQ-PHYS-ENCODING: Encoding limited to OOK-NRZ and Manchester
# REQ-PHYS-TPSL: Transmit power safety limits enforced across operations

CBAND_MIN_NM = 1530.0
CBAND_MAX_NM = 1565.0
CHANNEL_SPACING_GHZ = 100.0

# Representative C-band reference frequency for ITU-T DWDM grid (THz) near C-band center
# This is used for discretization to 100 GHz spacing.
GRID_REF_THZ = 193.1

ALLOWED_MI = {0.0, 0.1, 0.2, 0.33, 0.8}


def _is_valid_cband_nm(wavelength_nm: float) -> bool:
    return CBAND_MIN_NM <= wavelength_nm <= CBAND_MAX_NM


def _nearest_100ghz_nm(wavelength_nm: float) -> Tuple[float, float]:
    """
    Compute the nearest ITU-T G.694 100 GHz grid wavelength (nm) to the requested wavelength.

    Returns:
        (nearest_nm, delta_nm) where delta_nm = requested - nearest (signed).
    """
    # Convert nm -> THz, quantize to nearest 0.1 THz step (100 GHz), convert back to nm.
    c_nm_thz = 299_792.458
    if wavelength_nm <= 0:
        raise ValueError("wavelength must be positive")
    freq_thz = c_nm_thz / wavelength_nm
    k = round((freq_thz - GRID_REF_THZ) / 0.1)
    nearest_thz = GRID_REF_THZ + 0.1 * k
    nearest_nm = c_nm_thz / nearest_thz
    return nearest_nm, wavelength_nm - nearest_nm


class LaserConfig(BaseModel):
    """
    Laser configuration surface for GET/POST /laser/config.

    Note:
    - wavelength_nm must be within 1530–1565 nm and lie on the exact 100 GHz grid per ITU-T G.694
      (REQ-OPT-CBAND-100GHZ). If not aligned, the request is rejected with the nearest valid channel hint.
    - power must adhere to TPSL enforcement (REQ-PHYS-TPSL).
    - modulationIndex constrained to approved discrete set.
    """
    wavelength_nm: float = Field(
        1550.12, description="Requested optical wavelength (nm), must align to 100 GHz DWDM grid."
    )
    power: float = Field(0.5, ge=0.0, le=2.5, description="Output optical power (W)")
    modulationIndex: float = Field(0.2, description="AM modulation index [0..1, bounded to enumerated set]")

    @validator("wavelength_nm")
    def _validate_wavelength(cls, v: float) -> float:
        if not _is_valid_cband_nm(v):
            raise ValueError(
                "REQ-OPT-CBAND-100GHZ: wavelength must be within 1530–1565 nm."
            )
        nearest, delta = _nearest_100ghz_nm(v)
        # Treat aligned if within a very small tolerance around exact grid
        if abs(delta) > 1e-6:
            raise ValueError(
                f"REQ-OPT-CBAND-100GHZ: wavelength {v:.4f} nm is not on 100 GHz grid. "
                f"Nearest valid channel: {nearest:.4f} nm"
            )
        return float(v)

    @validator("modulationIndex")
    def _validate_mi(cls, v: float) -> float:
        if v not in ALLOWED_MI:
            raise ValueError(
                f"REQ-PHYS-AM-TONE: modulationIndex must be one of {sorted(ALLOWED_MI)}"
            )
        return float(v)


class AMConfig(BaseModel):
    """Amplitude modulation tracking tone configuration."""
    enabled: bool = Field(True, description="Enable/disable tracking tone")
    frequency: Literal[40, 50] = Field(40, description="Tracking tone frequency (kHz). "
                                                      "REQ-PHYS-AM-TONE: allow 40 or 50 only.")
    modulationIndex: float = Field(0.2, description="AM modulation index [bounded list]")

    @validator("modulationIndex")
    def _validate_mi(cls, v: float) -> float:
        if v not in ALLOWED_MI:
            raise ValueError(
                f"REQ-PHYS-AM-TONE: modulationIndex must be one of {sorted(ALLOWED_MI)}"
            )
        return float(v)


class TPSLConfig(BaseModel):
    """Transmitted Power Safety Limit configuration for /power/tpsl."""
    limit: float = Field(2.5, ge=0.0, description="Max transmit power (W)")
    enforced: bool = Field(True, description="Whether to enforce the limit (REQ-PHYS-TPSL).")


class EncodingConfig(BaseModel):
    """Encoding configuration to select OOK-NRZ or Manchester (REQ-PHYS-ENCODING)."""
    encoding: Literal["OOK-NRZ", "Manchester"] = Field(
        "OOK-NRZ", description="Encoding selection for payload signaling."
    )
    # Placeholder for future parameters if needed
    am: Optional[AMConfig] = Field(default=None, description="Optional AM override")
