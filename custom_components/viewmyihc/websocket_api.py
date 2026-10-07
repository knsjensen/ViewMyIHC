"""Websocket commands used by the ViewMyIHC panel (admin users only)."""

from __future__ import annotations

import logging
from pathlib import Path
import time
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from . import project_backup
from .admin_reader import read_admin
from .const import DOMAIN, MAX_VALUE_IDS, VERSION
from .ihc_bridge import (
    BridgeError,
    fetch_project_xml,
    find_controllers,
    project_signature,
    resource_state,
    runtime_values,
    write_value,
)
from .project_parser import VIEWS, Project, ProjectError
from .value_hold import Holds

_LOGGER = logging.getLogger(__name__)

_VIEW = vol.In(VIEWS)



def _store(hass: HomeAssistant) -> dict[str, Any]:
    return hass.data.setdefault(DOMAIN, {"projects": {}})


def _controller(hass: HomeAssistant, serial: str | None) -> tuple[str, Any]:
    controllers = find_controllers(hass.data)
    if not controllers:
        raise BridgeError("no_ihc")
    if serial is None:
        serial = next(iter(controllers))
    if serial not in controllers:
        raise BridgeError(f"Unknown controller {serial}")
    return serial, controllers[serial]


def _loaded(hass: HomeAssistant, serial: str) -> Project:
    cached = _store(hass)["projects"].get(serial)
    if cached is None:
        raise BridgeError("not_loaded")
    return cached["project"]


def _load_blocking(
    controller: Any, cached: dict[str, Any] | None, force: bool, backups: Path | None = None, serial: str = ""
) -> dict[str, Any]:
    signature = project_signature(controller)
    if cached is not None and cached["signature"] == signature and not force:
        return cached
    xml = fetch_project_xml(controller)
    project = Project(xml)
    if backups is not None:
        info = {key: project.info.get(key) for key in ("modified", "description", "resources", "version")}
        try:
            project_backup.save(backups, serial, xml, info)
        except OSError:  # a backup that cannot be written must never stop the panel
            _LOGGER.warning("ViewMyIHC: could not store a backup of the project", exc_info=True)
    return {"project": project, "signature": signature}


def _fail(connection: websocket_api.ActiveConnection, msg_id: int, err: Exception) -> None:
    code = "no_ihc" if str(err) == "no_ihc" else "not_loaded" if str(err) == "not_loaded" else "ihc_error"
    if code == "ihc_error":
        _LOGGER.warning("ViewMyIHC: %s", err)
    connection.send_error(msg_id, code, str(err))


@callback
def async_register(hass: HomeAssistant) -> None:
    """Register all commands."""
    for handler in (
        ws_status, ws_load, ws_children, ws_detail, ws_search, ws_values, ws_resource, ws_set, ws_hold,
        ws_admin_snapshot, ws_admin_refresh,
    ):
        websocket_api.async_register_command(hass, handler)


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/status"})
@websocket_api.require_admin
@callback
def ws_status(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Which controllers exist and which projects are already loaded."""
    controllers = find_controllers(hass.data)
    projects = _store(hass)["projects"]
    connection.send_result(
        msg["id"],
        {
            # the panel compares this with its own version: after an update Home Assistant must be restarted
            # before the new Python code is used, and an old backend with a new panel breaks silently
            "version": VERSION,
            "controllers": [
                {"serial": serial, "loaded": serial in projects,
                 "ha_user": str(getattr(controller.client, "username", "") or "")}
                for serial, controller in controllers.items()
            ],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/load",
        vol.Optional("controller"): str,
        vol.Optional("force", default=False): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_load(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Load (or refresh) the project from the controller. Re-downloads only when the revision changed."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        projects = _store(hass)["projects"]
        entry = await hass.async_add_executor_job(
            _load_blocking, controller, projects.get(serial), msg["force"],
            Path(hass.config.path(".storage", "viewmyihc_backups")), serial,
        )
    except (BridgeError, ProjectError) as err:
        _fail(connection, msg["id"], err)
        return
    projects[serial] = entry
    from .tools_api import prefetch_product_images  # noqa: PLC0415 - tools_api imports this module

    prefetch_product_images(hass, controller, entry["project"])
    connection.send_result(msg["id"], {"controller": serial, "info": entry["project"].info})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/children",
        vol.Optional("controller"): str,
        vol.Required("parent"): int,
        vol.Optional("view", default="all"): _VIEW,
    }
)
@websocket_api.require_admin
@callback
def ws_children(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], project.children(msg["parent"], msg["view"]))


@websocket_api.websocket_command(
    {vol.Required("type"): "viewmyihc/detail", vol.Optional("controller"): str, vol.Required("ihc_id"): int}
)
@websocket_api.require_admin
@callback
def ws_detail(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    detail = project.detail(msg["ihc_id"])
    if detail is None:
        connection.send_error(msg["id"], "not_found", "Unknown node")
        return
    connection.send_result(msg["id"], detail)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/search",
        vol.Optional("controller"): str,
        vol.Required("query"): str,
        vol.Optional("view", default="all"): _VIEW,
    }
)
@websocket_api.require_admin
@callback
def ws_search(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    try:
        serial, _ = _controller(hass, msg.get("controller"))
        project = _loaded(hass, serial)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], project.search(msg["query"], msg["view"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/values",
        vol.Optional("controller"): str,
        vol.Required("ids"): [int],
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_values(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Live values for the resources currently visible in the panel (read only)."""
    ids = list(dict.fromkeys(msg["ids"]))[:MAX_VALUE_IDS]
    try:
        _, controller = _controller(hass, msg.get("controller"))
        values = await hass.async_add_executor_job(runtime_values, controller, ids)
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], {str(key): value for key, value in values.items()})


def _holds(hass: HomeAssistant) -> Holds:
    store = _store(hass)
    if "holds" not in store:
        store["holds"] = Holds(hass)
    return store["holds"]


def _enum_names(hass: HomeAssistant, serial: str, resource_id: int) -> dict[int, str] | None:
    """Names of an enum resource's choices, from the loaded project (None when unknown)."""
    entry = _store(hass)["projects"].get(serial)
    detail = entry["project"].detail(resource_id) if entry else None
    if not detail or not detail.get("enum"):
        return None
    return {value["id"]: value["name"] for value in detail["enum"]["values"]}


@websocket_api.websocket_command(
    {vol.Required("type"): "viewmyihc/resource", vol.Optional("controller"): str, vol.Required("ihc_id"): int}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_resource(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Runtime and initial value of one resource, with type and limits, for the controls in the detail panel."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        state = await hass.async_add_executor_job(resource_state, controller, msg["ihc_id"])
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], {**state, "holding": _holds(hass).active(serial, msg["ihc_id"])})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/set",
        vol.Optional("controller"): str,
        vol.Required("ihc_id"): int,
        vol.Required("value"): vol.Any(bool, int, float, str),
        vol.Optional("target", default="runtime"): vol.In(("runtime", "initial")),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_set(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Write the runtime value, or the initial value the controller starts with, and answer with both read back."""
    resource_id = msg["ihc_id"]
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        if _holds(hass).active(serial, resource_id):
            raise BridgeError("The value is being held – release the button first")
        state = await hass.async_add_executor_job(
            lambda: write_value(
                controller, resource_id, msg["value"],
                runtime=msg["target"] == "runtime", enum_names=_enum_names(hass, serial, resource_id),
            )
        )
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_value", str(err))
        return
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    _LOGGER.info("ViewMyIHC: %s value of resource %s set to %r", msg["target"], resource_id, msg["value"])
    connection.send_result(msg["id"], {**state, "holding": False})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/hold",
        vol.Optional("controller"): str,
        vol.Required("ihc_id"): int,
        vol.Required("action"): vol.In(("start", "keep", "release")),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_hold(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Hold-to-change for on/off values: ``start`` flips it, ``keep`` every second, ``release`` puts it back."""
    holds, resource_id = _holds(hass), msg["ihc_id"]
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        if msg["action"] == "start":
            result = {"holding": True, "value": await holds.start(serial, controller, resource_id)}
        elif msg["action"] == "keep":
            result = {"holding": holds.keep(serial, resource_id)}
        else:
            result = {"holding": False, "value": await holds.release(serial, resource_id)}
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], result)


def _snapshots(hass: HomeAssistant):
    return _store(hass)["admin_snapshots"]


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/admin/snapshot", vol.Optional("controller"): str})
@websocket_api.require_admin
@callback
def ws_admin_snapshot(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The last saved admin settings. Answers at once and never contacts the controller."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    sections = _snapshots(hass).sections(serial)
    connection.send_result(
        msg["id"],
        {
            "sections": sections,
            "saved": _snapshots(hass).get(serial)["saved"] if sections else None,
            # the user the ihc integration logs in with: the panel protects it (see admin_writer)
            "ha_user": str(getattr(controller.client, "username", "") or ""),
        },
    )


@websocket_api.websocket_command({vol.Required("type"): "viewmyihc/admin/refresh", vol.Optional("controller"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_admin_refresh(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Read the settings from the controller, compare with the saved state, save, and report the differences.

    The controller has no "changed" marker for these settings (only the project has a revision), so the whole
    set is read (11 small calls); the panel shows the saved state meanwhile, so nobody waits for it.
    Secrets are removed before anything is returned or stored.
    """
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        fresh = await hass.async_add_executor_job(read_admin, controller)
        result = await _snapshots(hass).async_apply(serial, fresh, time.time())
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    connection.send_result(msg["id"], result)
