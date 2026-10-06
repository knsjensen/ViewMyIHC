"""The last known state of the controller's admin settings, kept on disk.

Opening the Administration tab shows this at once (no waiting for the controller); a background read then
updates it and reports what changed. Secrets (passwords) are removed before anything gets here.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .admin_diff import merge_refresh

STORAGE_KEY = "viewmyihc.admin"
STORAGE_VERSION = 1
# only "volatile" values (uptime, clock) changed: rewrite the file at most this often
REWRITE_AFTER = 3600


class AdminSnapshotStore:
    """Per controller: ``{"saved": epoch, "sections": {key: section}}``."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, dict[str, Any]] = {}
        self._persisted_at: dict[str, float] = {}

    async def async_load(self) -> None:
        data = await self._store.async_load()
        self._data = dict((data or {}).get("controllers", {}))
        self._persisted_at = {serial: entry.get("saved", 0) for serial, entry in self._data.items()}

    def get(self, serial: str) -> dict[str, Any] | None:
        """The saved state, or ``None`` if this controller was never read."""
        return self._data.get(serial)

    def sections(self, serial: str) -> list[dict[str, Any]] | None:
        entry = self._data.get(serial)
        if entry is None:
            return None
        return [dict(section, fetched=entry["saved"]) for section in entry["sections"].values()]

    async def async_replace(self, serial: str, fresh: list[dict[str, Any]]) -> None:
        """Put sections just read after our own change into the saved state, so they are not reported as changes."""
        entry = self._data.get(serial)
        if entry is None:
            return
        for section in fresh:
            if "data" in section:
                entry["sections"][section["key"]] = section
        await self._store.async_save({"controllers": self._data})

    async def async_apply(self, serial: str, fresh: list[dict[str, Any]], now: float) -> dict[str, Any]:
        """Store a fresh read and report what changed compared with the saved state."""
        first = serial not in self._data
        saved = {} if first else self._data[serial]["sections"]
        show, keep, changes = merge_refresh(saved, fresh)
        new_sections = first or any(key not in saved for key in keep)
        self._data[serial] = {"saved": now, "sections": keep}
        if changes or new_sections or now - self._persisted_at.get(serial, 0) > REWRITE_AFTER:
            self._persisted_at[serial] = now
            await self._store.async_save({"controllers": self._data})
        return {
            "first": first,
            "changes": changes,
            "sections": [dict(section, fetched=now) for section in show],
            "errors": [{"key": s["key"], "error": s["error"]} for s in show if "error" in s],
            "fetched": now,
        }
