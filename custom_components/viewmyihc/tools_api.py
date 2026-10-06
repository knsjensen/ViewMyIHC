"""Websocket commands for the diagnostic tools: controller log, messages, dataline, coverage, press automation,
project backups/diff and the live monitor. All read-only towards the controller; admin users only."""

from __future__ import annotations

import base64
import logging
import time
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from . import controller_info, project_backup, scene_project
from .dataline_cache import DatalineCache
from .dataline_layout import layout
from .event_monitor import EventMonitor
from .ihc_bridge import BridgeError
from .press_automation import press_automation
from .project_diff import diff
from .project_parser import Project, ProjectError
from .product_images import ProductImages
from .report_builder import REPORTS
from .wiring_map import wiring
from .admin_api import WrongPassword, _check_password
from .websocket_api import _controller, _fail, _loaded, _store

_LOGGER = logging.getLogger(__name__)


def backup_root(hass: HomeAssistant) -> Path:
    return Path(hass.config.path(".storage", "viewmyihc_backups"))


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (
        ws_scene_messages, ws_map, ws_map_images, ws_report, ws_log, ws_log_clear, ws_messages, ws_dataline, ws_coverage, ws_press, ws_backups, ws_backup_diff, ws_backup_download,
        ws_monitor_start, ws_monitor_events, ws_monitor_clear,
    ):
        websocket_api.async_register_command(hass, handler)


def _command(name: str, schema: dict[Any, Any] | None = None):
    return websocket_api.websocket_command(
        {vol.Required("type"): f"viewmyihc/{name}", vol.Optional("controller"): str, **(schema or {})}
    )


@_command("scene/messages", {vol.Optional("refresh", default=False): bool})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_scene_messages(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Who gets messages on which resource, and who may control the controller by e-mail/SMS (SceneDesign, read-only)."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    cache = _store(hass).setdefault("scene_cache", {})
    try:
        result = await hass.async_add_executor_job(scene_project.read, controller, None if msg["refresh"] else cache.get(serial))
    except (BridgeError, scene_project.SceneProjectError) as err:
        _fail(connection, msg["id"], err)
        return
    cache[serial] = result
    entry = _store(hass)["projects"].get(serial)
    project: Project | None = entry["project"] if entry else None

    def resource(rid: int | None) -> dict[str, Any]:
        node = project.nodes.get(rid) if project is not None and rid is not None else None
        return {"id": rid, "name": node.name if node else None, "label": project.label(rid) if node else None}

    def slots(numbers: list[int]) -> list[dict[str, Any]]:
        book = project.sms_numbers if project is not None else {}
        return [{"slot": n, **book.get(n, {"number": "", "label": ""})} for n in numbers]

    out = {k: v for k, v in result.items() if k not in ("notifications", "controls")}
    out["notifications"] = [{**n, "resource": resource(n["resource"]), "slots": slots(n["slots"])} for n in result["notifications"]]
    out["controls"] = [{**c, "resource": resource(c["resource"]), "senders": slots(c["senders"]) if c["channel"] == "sms" else c["senders"]}
                       for c in result["controls"]]
    connection.send_result(msg["id"], out)


@_command("map")
@websocket_api.require_admin
@websocket_api.async_response
async def ws_map(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Modules, terminals and the products wired to them, for the wiring map (from the project only)."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    result = await hass.async_add_executor_job(wiring, project)
    connection.send_result(msg["id"], {**result, "info": project.info, "serial": serial})


@_command("map/images", {vol.Required("identifiers"): [str]})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_map_images(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """LK's product pictures from the controller's report pages (cached on disk; None where the controller has none)."""
    try:
        _, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    store = _store(hass)
    if "product_images" not in store:
        store["product_images"] = ProductImages(Path(hass.config.path(".storage", "viewmyihc_images")))
    images = await hass.async_add_executor_job(store["product_images"].get, controller, msg["identifiers"][:100])
    connection.send_result(msg["id"], {"images": images})


@_command("report", {vol.Required("report"): vol.In(tuple(REPORTS)), vol.Optional("only_marked", default=True): bool})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_report(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The content of one documentation report, built from the loaded project (no controller call)."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    builder = REPORTS[msg["report"]]
    args = (project, msg["only_marked"]) if msg["report"] == "function" else (project,)
    result = await hass.async_add_executor_job(builder, *args)
    connection.send_result(msg["id"], {**result, "info": project.info})


@_command("log", {vol.Optional("language", default="da"): vol.In(controller_info.LANGUAGES)})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_log(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The controller's user log."""
    try:
        _, controller = _controller(hass, msg.get("controller"))
        lines = await hass.async_add_executor_job(controller_info.user_log, controller, msg["language"])
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], {"lines": lines})


@_command("messages")
@websocket_api.require_admin
@websocket_api.async_response
async def ws_messages(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Sent SMS/e-mail notifications and the e-mail control log (each may fail on its own)."""
    try:
        _, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    result: dict[str, Any] = {"errors": {}, "control_disabled": False}
    try:
        result["notifications"] = await hass.async_add_executor_job(controller_info.notifications, controller)
    except BridgeError as err:
        result["notifications"], result["errors"]["notifications"] = [], str(err)
    result["control"] = []
    try:
        if await hass.async_add_executor_job(controller_info.control_enabled, controller):
            result["control"] = await hass.async_add_executor_job(controller_info.control_log, controller)
        else:
            result["control_disabled"] = True
    except BridgeError as err:
        result["errors"]["control"] = str(err)
    connection.send_result(msg["id"], result)


@_command("log/clear", {vol.Required("what"): vol.In(tuple(controller_info.CLEAR)), vol.Required("auth"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_log_clear(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Empty one of the controller's logs, like IHC Administrator's clear buttons. Needs the ihc login password."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        _check_password(serial, controller, msg["auth"])
        await hass.async_add_executor_job(controller_info.clear, controller, msg["what"])
    except WrongPassword as err:
        connection.send_error(msg["id"], "wrong_password", str(err))
        return
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    _LOGGER.info("ViewMyIHC: emptied the controller's %s", msg["what"])
    connection.send_result(msg["id"], {"cleared": msg["what"]})


@_command("dataline", {vol.Optional("refresh", default=False): bool})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_dataline(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Dataline lines with their module and slots.

    Without ``refresh`` this answers at once from the project and the saved copy of the controller's address lists
    (which only add the resource ids of free addresses). With ``refresh`` the controller is read, compared with the
    saved copy and saved; ``changed`` tells the panel whether anything is different.
    """
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    store = _store(hass)
    if "dataline_cache" not in store:
        store["dataline_cache"] = DatalineCache(hass)
    cache = store["dataline_cache"]
    saved = await cache.async_get(serial)
    result: dict[str, Any] = {"controller_error": None, "changed": False}
    if msg["refresh"]:
        try:
            found = await hass.async_add_executor_job(controller_info.dataline, controller)
        except BridgeError as err:
            result["controller_error"] = str(err)
        else:
            now = time.time()
            result["changed"] = await cache.async_put(serial, found, now)
            saved = {"saved": now, "data": found}
    result["saved"] = saved["saved"] if saved else None
    connection.send_result(msg["id"], {**layout(project, saved["data"] if saved else None), **result})


@_command("coverage")
@websocket_api.require_admin
@callback
def ws_coverage(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """All shown resources (the panel marks which ones have an entity and which are linked to nothing)."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], {"resources": project.resources()})


@_command(
    "press",
    {
        vol.Required("entity_id"): str,
        vol.Optional("name", default=""): str,
        vol.Optional("long_ms", default=800): int,
        vol.Optional("double_ms", default=400): int,
        vol.Optional("language", default="en"): vol.In(("da", "en")),
    },
)
@websocket_api.require_admin
@callback
def ws_press(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Automation YAML for short/long/double press of a binary sensor."""
    try:
        text = press_automation(msg["entity_id"], msg["name"], msg["long_ms"], msg["double_ms"], msg["language"])
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_value", str(err))
        return
    connection.send_result(msg["id"], {"yaml": text})


@_command("backups")
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backups(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    try:
        serial, _ = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    entries = await hass.async_add_executor_job(project_backup.list_backups, backup_root(hass), serial)
    connection.send_result(msg["id"], {"backups": [{k: v for k, v in e.items() if k != "sha256"} for e in entries]})


def _diff_blocking(root: Path, serial: str, old: str, new: str) -> dict[str, Any]:
    return diff(Project(project_backup.read(root, serial, old)), Project(project_backup.read(root, serial, new)))


@_command("backup/diff", {vol.Required("old"): str, vol.Required("new"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backup_diff(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """What changed from backup ``old`` to backup ``new``."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        result = await hass.async_add_executor_job(_diff_blocking, backup_root(hass), serial, msg["old"], msg["new"])
    except (BridgeError, project_backup.BackupError, ProjectError) as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], result)


@_command("backup/download", {vol.Required("name"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backup_download(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The stored file (gzip, base64); the panel unpacks it to a .vis file IHC Visual opens."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        data = await hass.async_add_executor_job(project_backup.read_gzip, backup_root(hass), serial, msg["name"])
    except (BridgeError, project_backup.BackupError) as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], {"name": msg["name"].removesuffix(".gz"), "gzip": base64.b64encode(data).decode()})


def _monitor(hass: HomeAssistant, serial: str) -> EventMonitor:
    return _store(hass).setdefault("monitors", {}).setdefault(serial, EventMonitor())


def _monitor_state(monitor: EventMonitor) -> dict[str, Any]:
    return {"started": monitor.started, "watching": monitor.watching}


@_command("monitor/start")
@websocket_api.require_admin
@websocket_api.async_response
async def ws_monitor_start(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Start recording changes of every shown resource (until Home Assistant restarts)."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
        monitor = _monitor(hass, serial)
        ids = [r["id"] for r in project.resources()]
        await hass.async_add_executor_job(monitor.start, controller, ids)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], _monitor_state(monitor))


@_command("monitor/events", {vol.Optional("after", default=0): int})
@websocket_api.require_admin
@callback
def ws_monitor_events(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Changes recorded after sequence number ``after``, with names from the loaded project."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    monitor = _monitor(hass, serial)
    entry = _store(hass)["projects"].get(serial)
    project: Project | None = entry["project"] if entry else None
    events = monitor.events(msg["after"])
    if project is not None:
        for event in events:
            node = project.nodes.get(event["id"])
            if node is not None:
                event.update(name=node.name, label=project.label(node.id), kind=node.value_kind)
    connection.send_result(msg["id"], {**_monitor_state(monitor), "events": events})


@_command("monitor/clear")
@websocket_api.require_admin
@callback
def ws_monitor_clear(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    try:
        serial, _ = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    _monitor(hass, serial).clear()
    connection.send_result(msg["id"], _monitor_state(_monitor(hass, serial)))
