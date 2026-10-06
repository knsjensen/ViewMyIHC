"""Websocket commands about the entities of the built-in ``ihc`` integration (admin users only, all read only).

ViewMyIHC never creates entities and never writes files. It lists what exists, suggests which list a resource belongs in
and renders the YAML entry the user pastes into their own ``ihc:`` configuration.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .config_locator import check_setup, placement
from .const import IHC_DOMAIN
from .entity_config import EntityConfigError, render_entry, suggest, validate_entry
from .ihc_bridge import BridgeError
from .websocket_api import _controller, _fail, _loaded

DEVICE_CLASSES = frozenset(c.value for c in BinarySensorDeviceClass)

_ENTRY = vol.Schema(
    {
        vol.Required("platform"): str,
        vol.Required("id"): vol.Any(int, str),
        vol.Optional("name"): vol.Any(str, None),
        vol.Optional("note"): vol.Any(str, None),
        vol.Optional("position"): vol.Any(str, None),
        vol.Optional("options"): dict,
    }
)


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (ws_suggest, ws_list, ws_existing, ws_snippet, ws_check):
        websocket_api.async_register_command(hass, handler)


async def _setup(hass: HomeAssistant, controller: Any) -> dict[str, Any]:
    """The setup check for the connected controller (runs in the executor: it reads files)."""
    url = getattr(getattr(controller, "client", None), "url", None)
    return await hass.async_add_executor_job(check_setup, hass.config.config_dir, url)


def existing_entities(hass: HomeAssistant, serial: str, setup: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    """Which IHC resources already have an entity in the ``ihc`` integration, by resource id.

    Two sources: entities Home Assistant already created (entity registry: platform ``ihc``, unique id
    ``<serial>-<ihc id>``, whether they came from YAML or the integration's auto setup) and entries in the user's
    YAML that have not been loaded yet (they appear after the next restart).
    """
    found: dict[int, list[dict[str, Any]]] = {}
    prefix = f"{serial}-"
    for entry in er.async_get(hass).entities.values():
        if entry.platform != IHC_DOMAIN or not (entry.unique_id or "").startswith(prefix):
            continue
        try:
            ihc_id = int(entry.unique_id[len(prefix):])
        except ValueError:
            continue
        found.setdefault(ihc_id, []).append(
            {
                "source": "registry",
                "entity_id": entry.entity_id,
                "platform": entry.domain,
                "name": entry.name or entry.original_name or entry.entity_id,
                "disabled": entry.disabled_by is not None,
                "area_id": entry.area_id,
            }
        )
    for platform, info in (setup.get("platforms") or {}).items():
        for item in info["entries"]:
            known = found.setdefault(item["id"], [])
            if not any(k["platform"] == platform for k in known):
                known.append(
                    {"source": "yaml", "entity_id": None, "platform": platform, "name": item.get("name") or f"ihc_{item['id']}",
                     "disabled": False, "area_id": None, "file": item["file"], "line": item["line"]}
                )
    return found


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/entity/list", vol.Optional("controller"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_list(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Every entity of the ihc integration (and every YAML entry still waiting for a restart), one row each."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    setup = await _setup(hass, controller)
    found = existing_entities(hass, serial, setup)
    rows = [dict(item, ihc_id=ihc_id) for ihc_id, items in found.items() for item in items]
    rows.sort(key=lambda r: (r["platform"], r["ihc_id"]))
    connection.send_result(msg["id"], {"entities": rows, "count": len(rows)})


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/entity/existing", vol.Optional("controller"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_existing(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Resources that already exist as entities in the ihc integration (to flag them in the tree)."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    found = existing_entities(hass, serial, await _setup(hass, controller))
    connection.send_result(msg["id"], {"by_id": {str(i): items for i, items in found.items()}, "count": len(found)})


@websocket_api.websocket_command(
    {vol.Required("type"): "viewmyihc/entity/suggest", vol.Optional("controller"): str, vol.Required("ihc_id"): int}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_suggest(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Which list a project resource belongs in, defaults for the form, and what already exists for it."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    detail = project.detail(msg["ihc_id"])
    if detail is None or not detail.get("kind"):
        connection.send_error(msg["id"], "not_found", "Not a resource")
        return
    result = suggest(detail)
    result["device_classes"] = sorted(DEVICE_CLASSES)
    result["existing"] = existing_entities(hass, serial, await _setup(hass, controller)).get(msg["ihc_id"], [])
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {vol.Required("type"): "viewmyihc/entity/snippet", vol.Optional("controller"): str, vol.Required("entry"): _ENTRY}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_snippet(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Render the YAML entry, say where it goes in the user's setup, and check that it does not exist already.

    Nothing is written. ``blocked`` is true when an entity of the same type already exists for the resource (a second
    one would be rejected by Home Assistant as a duplicate).
    """
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        entry = validate_entry(msg["entry"], DEVICE_CLASSES)
    except EntityConfigError as err:
        connection.send_result(msg["id"], {"ok": False, "errors": err.errors})
        return
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    setup = await _setup(hass, controller)
    existing = existing_entities(hass, serial, setup).get(entry["id"], [])
    same = [e for e in existing if e["platform"] == entry["platform"]]
    connection.send_result(
        msg["id"],
        {
            "ok": True,
            "yaml": render_entry(entry),
            "placement": placement(setup, entry["platform"], entry),
            "same_platform": same,
            "other_platforms": [e for e in existing if e["platform"] != entry["platform"]],
            "blocked": bool(same),
        },
    )


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/entity/check", vol.Optional("controller"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_check(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Where the ihc setup lives (file and line). Follows ``!include`` references; reads only, never ``secrets.yaml``."""
    try:
        _, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    try:
        connection.send_result(msg["id"], await _setup(hass, controller))
    except (OSError, ValueError) as err:
        connection.send_error(msg["id"], "check_failed", str(err))
