"""ViewMyIHC – browse the IHC project and controller settings from a Home Assistant panel."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Event, HomeAssistant

from . import admin_api, connection_guard, entity_api, settings, tools_api, websocket_api
from .admin_snapshot import AdminSnapshotStore
from .const import DOMAIN, PANEL_COMPONENT, PANEL_URL_PATH, STATIC_URL

_FRONTEND_DIR = Path(__file__).parent / "frontend"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register the websocket API and the sidebar panel."""
    store = hass.data.setdefault(DOMAIN, {"projects": {}})
    if not store.get("registered"):
        websocket_api.async_register(hass)
        entity_api.async_register(hass)
        tools_api.async_register(hass)
        admin_api.async_register(hass)
        settings.async_register(hass)
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(_FRONTEND_DIR), cache_headers=False)]
        )
        store["registered"] = True
    if "settings" not in store:
        store["settings"] = settings.Settings(hass)
        await store["settings"].async_load()
    store["settings"].apply()

    async def _apply_when_started(_event: Event) -> None:
        # the ihc integration may only have finished its setup now
        if "settings" in hass.data.get(DOMAIN, {}):
            hass.data[DOMAIN]["settings"].apply()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _apply_when_started))
    if "admin_snapshots" not in store:
        store["admin_snapshots"] = AdminSnapshotStore(hass)
        await store["admin_snapshots"].async_load()

    # a changing query string makes browsers pick up a new panel script after an update
    version = (_FRONTEND_DIR / "viewmyihc-panel.js").stat().st_mtime_ns
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_COMPONENT,
        frontend_url_path=PANEL_URL_PATH,
        module_url=f"{STATIC_URL}/viewmyihc-panel.js?v={version}",
        sidebar_title="ViewMyIHC",
        sidebar_icon="mdi:home-automation",
        require_admin=True,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove the panel (the websocket commands stay registered until restart)."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
    data = hass.data.get(DOMAIN, {})
    if "settings" in data:  # hand the ihc connection back exactly as ihcsdk made it
        for controller in websocket_api.find_controllers(hass.data).values():
            connection_guard.remove(controller)
        data.pop("settings")
    if "holds" in data:
        await data.pop("holds").release_all()
    data.get("projects", {}).clear()
    data.pop("admin_snapshots", None)
    return True
