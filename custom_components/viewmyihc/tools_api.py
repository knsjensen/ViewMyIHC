"""Websocket commands for the diagnostic tools: controller log, messages, dataline, coverage, press automation,
project backups/diff and the live monitor. All read-only towards the controller; admin users only."""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from . import controller_info, project_backup, project_restore, scene_editor, scene_project
from .dataline_cache import DatalineCache
from .dataline_layout import layout
from .event_monitor import EventMonitor
from .ihc_bridge import BridgeError, fetch_project_xml
from .press_automation import press_automation
from .project_diff import diff
from .project_parser import Project, ProjectError
from .product_images import ProductImages
from .report_builder import REPORTS
from .wiring_map import wiring
from .admin_api import WrongPassword, _check_password
from .websocket_api import _controller, _fail, _holds, _load_blocking, _loaded, _store

_LOGGER = logging.getLogger(__name__)


def backup_root(hass: HomeAssistant) -> Path:
    return Path(hass.config.path(".storage", "viewmyihc_backups"))


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (
        ws_backup_restore, ws_scene_messages, ws_scene_test, ws_scene_save, ws_map, ws_map_images, ws_report, ws_log, ws_log_clear, ws_messages, ws_dataline, ws_coverage, ws_press, ws_backups, ws_backup_diff, ws_backup_download,
        ws_monitor_start, ws_monitor_events, ws_monitor_clear,
    ):
        websocket_api.async_register_command(hass, handler)


def _command(name: str, schema: dict[Any, Any] | None = None):
    return websocket_api.websocket_command(
        {vol.Required("type"): f"viewmyihc/{name}", vol.Optional("controller"): str, **(schema or {})}
    )


async def _scene(hass: HomeAssistant, serial: str, controller: Any, refresh: bool) -> dict[str, Any]:
    """The parsed scene project (cached on the controller's checksum); a freshly downloaded one is also kept in Versions."""
    cache = _store(hass).setdefault("scene_cache", {})
    result = await hass.async_add_executor_job(scene_project.read, controller, None if refresh else cache.get(serial))
    icz = result.pop("icz", None)
    if icz is not None:
        info = {"scene_name": result.get("name"), "notifications": len(result["notifications"]),
                "controls": len(result["controls"]), "scenes": result["scenes"]}
        await hass.async_add_executor_job(project_backup.save_scene, backup_root(hass), serial, icz, info)
    cache[serial] = result
    return result


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
    try:
        result = await _scene(hass, serial, controller, msg["refresh"])
    except (BridgeError, scene_project.SceneProjectError) as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], _scene_view(hass, serial, result))


def _scene_view(hass: HomeAssistant, serial: str, result: dict[str, Any]) -> dict[str, Any]:
    """The parsed lists for the panel: resource names, SMS slots with numbers, the phone book and whether it may be edited."""
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
    out["phonebook"] = {str(slot): info for slot, info in (project.sms_numbers if project is not None else {}).items()}
    settings = _store(hass).get("settings")
    out["verified"] = bool(settings and serial in settings.values.get("scene_upload_verified", []))
    return out


def _scene_lock(hass: HomeAssistant) -> asyncio.Lock:
    return _store(hass).setdefault("restore_lock", asyncio.Lock())  # one write to the controller at a time


@_command("scene/test", {vol.Required("auth"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_scene_test(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Send the unchanged scene project back and check it; editing is allowed on this controller only after this."""
    lock = _scene_lock(hass)
    if lock.locked():
        connection.send_error(msg["id"], "busy", "Another change of the controller is running")
        return
    async with lock:
        try:
            serial, controller = _controller(hass, msg.get("controller"))
            _check_password(serial, controller, msg["auth"])
            info = await hass.async_add_executor_job(scene_project.project_info, controller)
            icz = await hass.async_add_executor_job(scene_project.download, controller, info)
            await hass.async_add_executor_job(project_backup.save_scene, backup_root(hass), serial, icz, {"note": "before test upload"})
            await hass.async_add_executor_job(project_restore.restore_scene, controller, icz)
        except WrongPassword as err:
            connection.send_error(msg["id"], "wrong_password", str(err))
            return
        except (project_restore.RestoreError, scene_project.SceneProjectError) as err:
            _LOGGER.warning("ViewMyIHC: test upload of the scene project failed: %s", err)
            connection.send_error(msg["id"], "restore_failed", str(err))
            return
        except BridgeError as err:
            _fail(connection, msg["id"], err)
            return
        settings = _store(hass).get("settings")
        if settings is not None:
            verified = sorted({*settings.values.get("scene_upload_verified", []), serial})
            await settings.async_update({"scene_upload_verified": verified})
    _LOGGER.warning("ViewMyIHC: test upload of the scene project succeeded; editing it is now allowed")
    connection.send_result(msg["id"], {"verified": True})


@_command("scene/save", {vol.Required("crc"): str, vol.Required("notifications"): [dict], vol.Required("controls"): [dict],
                         vol.Required("auth"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_scene_save(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Write new message/control lists to the SceneDesign project; a failed upload puts the previous one back."""
    lock = _scene_lock(hass)
    if lock.locked():
        connection.send_error(msg["id"], "busy", "Another change of the controller is running")
        return
    async with lock:
        try:
            serial, controller = _controller(hass, msg.get("controller"))
            _check_password(serial, controller, msg["auth"])
            settings = _store(hass).get("settings")
            if not settings or serial not in settings.values.get("scene_upload_verified", []):
                raise project_restore.RestoreError("Run the test upload first")
            info = await hass.async_add_executor_job(scene_project.project_info, controller)
            if str(info.get("crc") or "") != msg["crc"]:
                raise project_restore.RestoreError("The scene project was changed on the controller meanwhile - reload and try again")
            old = await hass.async_add_executor_job(scene_project.download, controller, info)
            new = scene_editor.apply(old, msg["notifications"], msg["controls"])
            if new != old:
                await hass.async_add_executor_job(project_backup.save_scene, backup_root(hass), serial, old, {"note": "before edit"})
                try:
                    await hass.async_add_executor_job(project_restore.restore_scene, controller, new)
                except (project_restore.RestoreError, BridgeError) as err:
                    try:  # put the previous project back
                        await hass.async_add_executor_job(project_restore.restore_scene, controller, old)
                    except (project_restore.RestoreError, BridgeError):
                        _LOGGER.exception("ViewMyIHC: could not put the previous scene project back")
                        raise project_restore.RestoreError(
                            f"{err} - the previous version could not be put back automatically; restore it under Versions") from err
                    raise project_restore.RestoreError(f"{err} - the previous version was put back") from err
            result = await _scene(hass, serial, controller, True)
        except WrongPassword as err:
            connection.send_error(msg["id"], "wrong_password", str(err))
            return
        except scene_editor.SceneEditError as err:
            connection.send_error(msg["id"], "invalid_value", str(err))
            return
        except (project_restore.RestoreError, scene_project.SceneProjectError) as err:
            connection.send_error(msg["id"], "restore_failed", str(err))
            return
        except BridgeError as err:
            _fail(connection, msg["id"], err)
            return
    _LOGGER.warning("ViewMyIHC: saved changed messages/controls in the SceneDesign project")
    connection.send_result(msg["id"], _scene_view(hass, serial, result))


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


@_command("backups", {vol.Optional("kind", default="ihc"): vol.In(("ihc", "scene"))})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backups(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Saved projects, newest first. For the scene project the controller is checked first (a changed one is saved)."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    error = None
    if msg["kind"] == "scene":
        try:
            await _scene(hass, serial, controller, False)
        except (BridgeError, scene_project.SceneProjectError) as err:
            error = str(err)  # the saved copies are still listed
    entries = await hass.async_add_executor_job(project_backup.list_backups, backup_root(hass), serial, msg["kind"])
    connection.send_result(msg["id"], {"backups": [{k: v for k, v in e.items() if k != "sha256"} for e in entries], "error": error})


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


@_command("backup/download", {vol.Required("name"): str, vol.Optional("kind", default="ihc"): vol.In(("ihc", "scene"))})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backup_download(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The stored file (gzip, base64); the panel unpacks it to a .vis file IHC Visual opens."""
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        if msg["kind"] == "scene":
            data = await hass.async_add_executor_job(project_backup.read_scene, backup_root(hass), serial, msg["name"])
        else:
            data = await hass.async_add_executor_job(project_backup.read_gzip, backup_root(hass), serial, msg["name"])
    except (BridgeError, project_backup.BackupError) as err:
        _fail(connection, msg["id"], err)
        return
    if msg["kind"] == "scene":  # an .icz is a zip already: handed over as it is
        connection.send_result(msg["id"], {"name": msg["name"], "data": base64.b64encode(data).decode()})
    else:
        connection.send_result(msg["id"], {"name": msg["name"].removesuffix(".gz"), "gzip": base64.b64encode(data).decode()})


@_command("backup/restore", {vol.Required("name"): str, vol.Optional("kind", default="ihc"): vol.In(("ihc", "scene")),
                              vol.Required("auth"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_backup_restore(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Send a saved version back to the controller. The current one is saved first, so the restore can be undone."""
    store = _store(hass)
    lock: asyncio.Lock = store.setdefault("restore_lock", asyncio.Lock())
    if lock.locked():
        connection.send_error(msg["id"], "busy", "A restore is already running")
        return
    async with lock:
        try:
            serial, controller = _controller(hass, msg.get("controller"))
            _check_password(serial, controller, msg["auth"])
            root = backup_root(hass)
            if msg["kind"] == "scene":
                icz = await hass.async_add_executor_job(project_backup.read_scene, root, serial, msg["name"])
                await _scene(hass, serial, controller, True)  # the current one is kept in Versions first
                await hass.async_add_executor_job(project_restore.restore_scene, controller, icz)
                store.setdefault("scene_cache", {}).pop(serial, None)
                result: dict[str, Any] = {"kind": "scene"}
            else:
                xml = await hass.async_add_executor_job(project_backup.read, root, serial, msg["name"])
                project_restore.check_project(xml)
                await _holds(hass).release_all()

                def keep_current() -> None:
                    current = fetch_project_xml(controller)
                    project_backup.save(root, serial, current, {"note": "before restore"})

                await hass.async_add_executor_job(keep_current)  # no copy of the current project: no restore
                final = await hass.async_add_executor_job(
                    project_restore.restore_project, controller, xml, msg["name"].removesuffix(".gz"))
                entry = await hass.async_add_executor_job(_load_blocking, controller, None, True, root, serial)
                store["projects"][serial] = entry
                result = {"kind": "ihc", "state": final, "info": entry["project"].info}
        except WrongPassword as err:
            connection.send_error(msg["id"], "wrong_password", str(err))
            return
        except (project_restore.RestoreError, project_backup.BackupError, scene_project.SceneProjectError) as err:
            _LOGGER.warning("ViewMyIHC: restore of %s failed: %s", msg["name"], err)
            connection.send_error(msg["id"], "restore_failed", str(err))
            return
        except BridgeError as err:
            _fail(connection, msg["id"], err)
            return
    _LOGGER.warning("ViewMyIHC: restored %s on the controller", msg["name"])
    connection.send_result(msg["id"], result)


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
