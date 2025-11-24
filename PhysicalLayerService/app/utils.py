from __future__ import annotations

from datetime import datetime, timezone
from typing import Union


# PUBLIC_INTERFACE
def nm_to_thz(wavelength_nm: float) -> float:
    """Convert wavelength (nm) to frequency (THz) using c=299792.458 nm*THz.

    Returns:
        Frequency in THz.
    """
    c_nm_thz = 299_792.458
    if wavelength_nm <= 0:
        raise ValueError("wavelength must be positive")
    return c_nm_thz / wavelength_nm


# PUBLIC_INTERFACE
def thz_to_nm(freq_thz: float) -> float:
    """Convert frequency (THz) to wavelength (nm)."""
    c_nm_thz = 299_792.458
    if freq_thz <= 0:
        raise ValueError("frequency must be positive")
    return c_nm_thz / freq_thz


# PUBLIC_INTERFACE
def utc_now() -> datetime:
    """Return current UTC datetime using system host clock."""
    return datetime.now(timezone.utc)


# PUBLIC_INTERFACE
def sync_timestamp_to_host(ts: Union[datetime, None] = None) -> datetime:
    """Placeholder for timestamp synchronization to host clock.

    If ts is provided, it is returned as-is normalized to UTC.
    Otherwise current UTC time is returned.

    Note: Future implementation can adjust using measured skew.
    """
    if ts is None:
        return utc_now()
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)
