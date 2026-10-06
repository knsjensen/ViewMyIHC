"""ViewMyIHC's own settings (kept in Home Assistant's storage) and applying them to the ihc controllers."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from . import connection_guard
from .const import DOMAIN
from .ihc_bridge import find_controllers

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = "viewmyihc.settings"
STORAGE_VERSION = 1
DEFAULTS: dict[str, Any] = {"ihc_timeout": False, "ihc_timeout_seconds": connection_guard.DEFAULT_SECONDS}


class Settings:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.values: dict[str, Any] = dict(DEFAULTS)

    async def async_load(self) -> None:
        self.values = {**DEFAULTS, **(await self._store.async_load() or {})}

    async def async_update(self, changes: dict[str, Any]) -> None:
        self.values.update({k: v for k, v in changes.items() if k in DEFAULTS})
        await self._store.async_save(self.values)
        self.apply()

    def apply(self) -> dict[str, int | None]:
        """Put the timeout on (or take it off) every ihc controller. Returns the timeout now active per controller."""
        result: dict[str, int | None] = {}
        for serial, controller in find_controllers(self._hass.data).items():
            if self.values["ihc_timeout"]:
                if connection_guard.apply(controller, self.values["ihc_timeout_seconds"]):
                    _LOGGER.debug("ViewMyIHC: timeout of %ss on the ihc connection to %s", self.values["ihc_timeout_seconds"], serial)
            else:
                connection_guard.remove(controller)
            result[serial] = connection_guard.active_timeout(controller)
        return result

    def status(self) -> dict[str, int | None]:
        return {serial: connection_guard.active_timeout(c) for serial, c in find_controllers(self._hass.data).items()}


# ------------------------------------------------------------------ websocket


def get_settings(hass: HomeAssistant) -> Settings:
    return hass.data[DOMAIN]["settings"]


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_settings_get)
    websocket_api.async_register_command(hass, ws_settings_set)


def _answer(settings: Settings) -> dict[str, Any]:
    return {"settings": settings.values, "active": settings.status(),
            "limits": {"min": connection_guard.MIN_SECONDS, "max": connection_guard.MAX_SECONDS}}


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/settings/get", vol.Optional("controller"): str})
@websocket_api.require_admin
@callback
def ws_settings_get(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], _answer(get_settings(hass)))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/settings/set",
        vol.Optional("controller"): str,  # the panel sends it with every command; settings are the same for all
        vol.Optional("ihc_timeout"): bool,
        vol.Optional("ihc_timeout_seconds"): vol.All(int, vol.Range(min=connection_guard.MIN_SECONDS, max=connection_guard.MAX_SECONDS)),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_settings_set(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    settings = get_settings(hass)
    await settings.async_update({k: v for k, v in msg.items() if k in DEFAULTS})
    _LOGGER.info("ViewMyIHC: settings changed: %s", {k: v for k, v in msg.items() if k in DEFAULTS})
    connection.send_result(msg["id"], _answer(settings))
