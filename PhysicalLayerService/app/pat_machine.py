from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from .models.pat_state import (
    PATRuntimeState,
    PATState,
    PATStateMachineConfig,
    PATStatus,
    Telemetry,
)
from .models.laser_params import AMConfig, LaserConfig, TPSLConfig
from .utils import utc_now

log = logging.getLogger(__name__)


@dataclass
class _LaserState:
    # Use default_factory to avoid mutable default instances being shared across class instances
    config: LaserConfig = field(default_factory=LaserConfig)
    am: AMConfig = field(default_factory=AMConfig)
    tpsl: TPSLConfig = field(default_factory=TPSLConfig)


class PATStateMachine:
    """In-memory PAT state machine with minimal behavior and safety checks."""

    def __init__(self) -> None:
        self._runtime = PATRuntimeState()
        self._laser = _LaserState()

    # PUBLIC_INTERFACE
    def initiate(self, cfg: PATStateMachineConfig) -> PATStatus:
        """Start the PAT sequence from standby/setup with provided configuration."""
        if self._runtime.state not in (PATState.STANDBY, PATState.PREPARE, PATState.STOP):
            raise ValueError(f"Cannot initiate PAT while in state {self._runtime.state}")

        self._runtime.config = cfg
        self._transition_to(PATState.SETUP)
        # After setup, proceed to coarse acquisition
        self._transition_to(PATState.COARSE_ACQ)
        return self.status()

    # PUBLIC_INTERFACE
    def stop(self) -> PATStatus:
        """Stop PAT, transitioning to STOP then STANDBY."""
        self._transition_to(PATState.STOP)
        # brief settle
        time.sleep(0.01)
        self._transition_to(PATState.STANDBY)
        return self.status()

    # PUBLIC_INTERFACE
    def status(self) -> PATStatus:
        """Get current PAT status."""
        return self._runtime.as_status()

    # PUBLIC_INTERFACE
    def telemetry(self) -> Telemetry:
        """Get a current telemetry snapshot."""
        return Telemetry(state=self._runtime.state)

    # PUBLIC_INTERFACE
    def proceed(self) -> PATStatus:
        """Advance state machine along nominal path."""
        nxt: Optional[PATState] = None
        cur = self._runtime.state
        if cur == PATState.COARSE_ACQ:
            nxt = PATState.FINE_ACQ
        elif cur == PATState.FINE_ACQ:
            nxt = PATState.COMMUNICATION
        elif cur == PATState.COMMUNICATION:
            # remain until stop
            nxt = None
        elif cur in (PATState.SETUP,):
            nxt = PATState.COARSE_ACQ
        elif cur in (PATState.STANDBY, PATState.PREPARE, PATState.STOP):
            nxt = PATState.SETUP

        if nxt:
            self._transition_to(nxt)
        return self.status()

    # PUBLIC_INTERFACE
    def set_laser_config(self, cfg: LaserConfig) -> LaserConfig:
        """Update laser configuration while enforcing TPSL."""
        if cfg.power > self._laser.tpsl.limit and self._laser.tpsl.enforced:
            raise ValueError("Requested power exceeds TPSL limit")
        self._laser.config = cfg
        return self._laser.config

    # PUBLIC_INTERFACE
    def get_laser_config(self) -> LaserConfig:
        """Return current laser configuration."""
        return self._laser.config

    # PUBLIC_INTERFACE
    def set_am_config(self, cfg: AMConfig) -> AMConfig:
        """Update AM tracking tone configuration."""
        self._laser.am = cfg
        return self._laser.am

    # PUBLIC_INTERFACE
    def get_am_config(self) -> AMConfig:
        """Return AM configuration."""
        return self._laser.am

    # PUBLIC_INTERFACE
    def set_tpsl(self, cfg: TPSLConfig) -> TPSLConfig:
        """Set Transmitted Power Safety Limit."""
        if cfg.limit < 0:
            raise ValueError("TPSL limit cannot be negative")
        self._laser.tpsl = cfg
        # adjust current power if over limit
        if cfg.enforced and self._laser.config.power > cfg.limit:
            log.warning("Reducing power to TPSL limit")
            self._laser.config.power = cfg.limit
        return self._laser.tpsl

    # PUBLIC_INTERFACE
    def get_tpsl(self) -> TPSLConfig:
        """Get current TPSL configuration."""
        return self._laser.tpsl

    def _transition_to(self, state: PATState) -> None:
        """Internal transition helper with logging/timestamps."""
        log.info("PAT transition: %s -> %s", self._runtime.state, state)
        self._runtime.state = state
        self._runtime.entry_time_monotonic = time.monotonic()
        self._runtime.entry_time_utc = utc_now()


# Singleton machine for the service lifecycle
_machine = PATStateMachine()


# PUBLIC_INTERFACE
def get_machine() -> PATStateMachine:
    """Return the module-level PAT state machine singleton."""
    return _machine
