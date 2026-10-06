"""Hold-to-change, like the space bar in IHC ServiceView: an on/off value is flipped while a button is held and
put back to what it was when the button is released.

The panel sends keep-alives while the button is down. When they stop (tab closed, network gone, browser asleep)
the value is put back by itself, so a lost connection can never leave an output switched.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .ihc_bridge import BridgeError, resource_state, send_value
from .resource_values import BOOL

_LOGGER = logging.getLogger(__name__)

# the panel sends a keep-alive every second; two missed ones end the hold
HOLD_TIMEOUT = 2.5
MAX_RELEASE_ATTEMPTS = 5


class Holds:
    """Active holds, keyed by (controller serial, resource id)."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._active: dict[tuple[str, int], dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def active(self, serial: str, resource_id: int) -> bool:
        return (serial, resource_id) in self._active

    async def start(self, serial: str, controller: Any, resource_id: int) -> bool:
        """Flip the value and keep it flipped. Returns the held value."""
        key = (serial, resource_id)
        async with self._lock:
            if key in self._active:
                self._arm(key)
                return self._active[key]["value"]
            state = await self._hass.async_add_executor_job(resource_state, controller, resource_id)
            current = state["runtime"]
            if current is None or current["type"] != BOOL:
                raise BridgeError("Only on/off values can be held")
            held = not current["value"]
            await self._hass.async_add_executor_job(
                lambda: send_value(controller, resource_id, current, held, runtime=True)
            )
            self._active[key] = {"controller": controller, "current": current, "original": current["value"], "value": held}
            self._arm(key)
            return held

    def keep(self, serial: str, resource_id: int) -> bool:
        """Extend a hold. False when it already ended (the panel then shows the button as released)."""
        key = (serial, resource_id)
        if key not in self._active:
            return False
        self._arm(key)
        return True

    async def release(self, serial: str, resource_id: int) -> bool | None:
        """Put the original value back. Returns it, or None when nothing was held."""
        key = (serial, resource_id)
        async with self._lock:
            hold = self._active.pop(key, None)
            if hold is None:
                return None
            hold["timer"].cancel()
            try:
                await self._hass.async_add_executor_job(
                    lambda: send_value(hold["controller"], resource_id, hold["current"], hold["original"], runtime=True)
                )
            except Exception:
                # the value is still flipped: keep the hold and try again shortly
                hold["failures"] = hold.get("failures", 0) + 1
                if hold["failures"] < MAX_RELEASE_ATTEMPTS:
                    self._active[key] = hold
                    self._arm(key)
                raise
            return hold["original"]

    async def release_all(self) -> None:
        for serial, resource_id in list(self._active):
            await self._release_quietly(serial, resource_id)

    def _arm(self, key: tuple[str, int]) -> None:
        hold = self._active[key]
        if hold.get("timer"):
            hold["timer"].cancel()
        hold["timer"] = self._hass.loop.call_later(
            HOLD_TIMEOUT, lambda: self._hass.async_create_task(self._release_quietly(*key))
        )

    async def _release_quietly(self, serial: str, resource_id: int) -> None:
        try:
            await self.release(serial, resource_id)
        except Exception:  # noqa: BLE001 - nobody is waiting for this answer, so log it
            _LOGGER.warning("ViewMyIHC: could not put resource %s back after a hold", resource_id, exc_info=True)
