"""The controller's dataline address lists, kept on disk so the Modules tab answers at once.

The lines and modules come from the project (already in memory); the controller only adds the resource ids of
free addresses. Those lists change only when the installation changes, so the panel shows the saved copy at once
and reads the controller in the background, like the admin settings.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

STORAGE_KEY = "viewmyihc.dataline"
STORAGE_VERSION = 1


class DatalineCache:
    """Per controller: ``{"saved": epoch, "data": {"inputs": [...], "outputs": [...]}}``."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, dict[str, Any]] | None = None

    async def async_get(self, serial: str) -> dict[str, Any] | None:
        if self._data is None:
            self._data = dict((await self._store.async_load() or {}).get("controllers", {}))
        return self._data.get(serial)

    async def async_put(self, serial: str, found: dict[str, Any], now: float) -> bool:
        """Remember a fresh read. Returns whether it differs from what was saved (the file is only rewritten then)."""
        previous = await self.async_get(serial)
        changed = previous is None or previous["data"] != found
        assert self._data is not None
        self._data[serial] = {"saved": now, "data": found}
        if changed:
            await self._store.async_save({"controllers": self._data})
        return changed
