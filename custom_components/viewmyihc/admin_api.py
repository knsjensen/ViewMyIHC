"""Websocket commands that change controller settings (admin users only). Each change is read back afterwards."""

from __future__ import annotations

import datetime
import hmac
import logging
import time
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from . import admin_writer
from .admin_reader import read_admin
from .ihc_bridge import BridgeError
from .websocket_api import _controller, _fail, _snapshots

_LOGGER = logging.getLogger(__name__)

# Every change needs the password of the user the ihc integration is logged in with, so one click in a browser that
# happens to be logged in to Home Assistant cannot reconfigure the controller. ihcsdk keeps that password in memory,
# so no file is read and the controller is not asked again.
MAX_FAILURES = 5
LOCKOUT = 300
_failures: dict[str, list[float]] = {}


class WrongPassword(Exception):
    pass


def _check_password(serial: str, controller: Any, given: str) -> None:
    now = time.monotonic()
    recent = [t for t in _failures.get(serial, []) if now - t < LOCKOUT]
    _failures[serial] = recent
    if len(recent) >= MAX_FAILURES:
        raise WrongPassword("Too many wrong passwords – try again in a few minutes")
    expected = str(getattr(controller.client, "password", "") or getattr(controller, "_password", "") or "")
    if not expected or not hmac.compare_digest(given.encode(), expected.encode()):
        recent.append(now)
        _LOGGER.warning("ViewMyIHC: wrong password for a change of the controller settings (%s of %s)", len(recent), MAX_FAILURES)
        raise WrongPassword("Wrong password")
    _failures.pop(serial, None)


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (ws_write, ws_dns, ws_email_control_enabled, ws_user):
        websocket_api.async_register_command(hass, handler)


async def _run(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any], section: str, job) -> None:
    """Run a change, read the section back, store it, answer with it. Errors keep the panel's form open."""
    try:
        serial, controller = _controller(hass, msg.get("controller"))
        _check_password(serial, controller, msg["auth"])
        result = await hass.async_add_executor_job(job, controller)
        fresh = await hass.async_add_executor_job(read_admin, controller, {section})
    except WrongPassword as err:
        connection.send_error(msg["id"], "wrong_password", str(err))
        return
    except admin_writer.NeedsConfirmation as err:
        connection.send_error(msg["id"], "needs_confirm", str(err))
        return
    except admin_writer.AdminWriteError as err:
        connection.send_error(msg["id"], "invalid_value", str(err))
        return
    except BridgeError as err:
        _fail(connection, msg["id"], err)
        return
    await _snapshots(hass).async_replace(serial, fresh)
    connection.send_result(msg["id"], {"changed": result, "sections": fresh})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/admin/write",
        vol.Optional("controller"): str,
        vol.Required("section"): vol.In(tuple(admin_writer.SPECS)),
        vol.Required("changes"): {str: vol.Any(str, int, bool, None)},
        vol.Optional("confirm", default=False): bool,
        vol.Optional("set_clock", default=False): bool,
        vol.Required("auth"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_write(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Change fields of network, SMTP, e-mail control, web access or time settings."""
    clock = datetime.datetime.now(datetime.timezone.utc) if msg["set_clock"] else None
    await _run(hass, connection, msg, msg["section"], lambda c: admin_writer.write_section(
        c, msg["section"], msg["changes"], confirm=msg["confirm"], set_clock=clock))


@websocket_api.websocket_command(
    {vol.Required("type"): "viewmyihc/admin/dns", vol.Optional("controller"): str,
     vol.Required("primary"): str, vol.Optional("secondary", default=""): str, vol.Required("auth"): str}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_dns(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _run(hass, connection, msg, "dns", lambda c: admin_writer.set_dns(c, msg["primary"], msg["secondary"]))


@websocket_api.websocket_command(
    {vol.Required("type"): "viewmyihc/admin/email_control_enabled", vol.Optional("controller"): str,
     vol.Required("enabled"): bool, vol.Required("auth"): str}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_email_control_enabled(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    await _run(hass, connection, msg, "email_control", lambda c: admin_writer.set_email_control_enabled(c, msg["enabled"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "viewmyihc/admin/user",
        vol.Optional("controller"): str,
        vol.Required("action"): vol.In(("add", "update", "remove")),
        vol.Required("username"): str,
        vol.Optional("password", default=""): str,
        vol.Optional("details", default={}): {vol.In(tuple(admin_writer.USER_FIELDS)): str},
        vol.Required("auth"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_user(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Add, change or remove a controller user."""
    action, name = msg["action"], msg["username"]
    if action == "add":
        def job(c):
            return admin_writer.add_user(c, name, msg["password"], msg["details"])
    elif action == "update":
        def job(c):
            return admin_writer.update_user(c, name, msg["password"] or None, msg["details"])
    else:
        def job(c):
            return admin_writer.remove_user(c, name)
    await _run(hass, connection, msg, "users", job)
