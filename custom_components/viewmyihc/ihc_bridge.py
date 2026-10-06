"""Borrow the already authenticated controller of Home Assistant's built-in ``ihc`` integration.

ViewMyIHC never sees or stores credentials: it only uses the ``IHCController`` object (and its SOAP
session) that the ``ihc`` integration created. All ihcsdk calls are blocking, so they must be run in
the executor by the caller.
"""

from __future__ import annotations

import contextlib
import datetime
import logging
from typing import Any

from . import resource_values
from .const import IHC_CONTROLLER_KEY, IHC_DOMAIN

_LOGGER = logging.getLogger(__name__)

STATE_READY = "text.ctrl.state.ready"


class BridgeError(Exception):
    """Raised for problems talking to the controller (message is shown in the panel)."""


def find_controllers(hass_data: dict[str, Any]) -> dict[str, Any]:
    """Return ``{serial: IHCController}`` for every controller set up by the ihc integration."""
    entries = hass_data.get(IHC_DOMAIN)
    if not isinstance(entries, dict):
        return {}
    return {
        str(serial): entry[IHC_CONTROLLER_KEY]
        for serial, entry in entries.items()
        if isinstance(entry, dict) and IHC_CONTROLLER_KEY in entry
    }


def _project_lock(controller: Any):
    """Class-level lock ihcsdk uses around authentication and project download.

    It is a plain (non-reentrant) ``threading.Lock`` and ``authenticate()`` takes it too, so it may
    only be held around calls that never authenticate. Ordinary SOAP reads do not need it.
    """
    return getattr(type(controller), "_mutex", None) or contextlib.nullcontext()


def json_value(value: Any) -> Any:
    """Make a runtime value JSON friendly."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        return int(value.total_seconds() * 1000)
    return str(value)


def soap_action(controller: Any, service: str, action: str, body: str = "") -> Any:
    """Call a SOAP action through the controller's own session. Returns the parsed XML or raises."""
    connection = controller.client.connection
    result = connection.soap_action(service, action, body)
    if result is False:
        # session probably expired: let the integration re-authenticate once (it takes the lock
        # itself, so we must not hold it here), then retry
        try:
            controller.re_authenticate(False)
        except Exception:  # noqa: BLE001 - ihcsdk raises assorted errors
            _LOGGER.debug("Re-authentication failed", exc_info=True)
        result = connection.soap_action(service, action, body)
    if result is False:
        raise BridgeError(f"{service}/{action} failed (no answer from the controller)")
    return result


def project_signature(controller: Any) -> str:
    """Cheap fingerprint of the project currently on the controller."""
    info = controller.client.get_project_info()
    if not info:
        raise BridgeError("Could not read project info from the controller")
    return repr(sorted((k, repr(v)) for k, v in info.items()))


def fetch_project_xml(controller: Any) -> str:
    """Download the project XML from the controller (in segments, like the ihc integration)."""
    with _project_lock(controller):
        state = controller.client.get_state()
        if state != STATE_READY:
            raise BridgeError(f"The controller is not ready (state: {state})")
        info = controller.client.get_project_info()
        xml = controller.client.get_project_in_segments(info) if info else False
    if not xml:
        raise BridgeError("The controller did not return a project")
    return xml


RESOURCES = "/ws/ResourceInteractionService"


def resource_state(controller: Any, resource_id: int) -> dict[str, Any]:
    """Runtime and initial value of one resource, typed as the controller reports them (two requests)."""
    rid = int(resource_id)
    runtime = soap_action(controller, RESOURCES, "getRuntimeValue", f'<getRuntimeValue1 xmlns="utcs">{rid}</getRuntimeValue1>')
    initial = soap_action(controller, RESOURCES, "getInitialValue", f'<getInitialValue1 xmlns="utcs">{rid}</getInitialValue1>')
    return {
        "runtime": resource_values.read_envelope(runtime, "getRuntimeValue2"),
        "initial": resource_values.read_envelope(initial, "getInitialValue2"),
    }


def write_value(
    controller: Any, resource_id: int, raw: Any, *, runtime: bool, enum_names: dict[int, str] | None = None
) -> dict[str, Any]:
    """Set the runtime or the initial value, then read both back so the panel shows what the controller holds.

    Raises ``ValueError`` for input that does not fit the resource and ``BridgeError`` when the controller refuses.
    """
    state = resource_state(controller, resource_id)
    current = state["runtime" if runtime else "initial"] or state["runtime"] or state["initial"]
    if current is None:
        raise BridgeError("The controller reported no value for this resource")
    value = resource_values.coerce(current, raw, set(enum_names) if enum_names is not None else None)
    send_value(controller, resource_id, current, value, runtime=runtime, enum_name=(enum_names or {}).get(value, ""))
    return resource_state(controller, resource_id)


def send_value(controller: Any, resource_id: int, current: dict[str, Any], value: Any, *, runtime: bool, enum_name: str = "") -> None:
    """One ``setResourceValue`` for an already checked value."""
    payload = resource_values.set_payload(resource_id, current, value, runtime=runtime, enum_name=enum_name)
    if not resource_values.accepted(soap_action(controller, RESOURCES, "setResourceValue", payload)):
        raise BridgeError("The controller refused the value")


def runtime_values(controller: Any, ids: list[int]) -> dict[int, Any]:
    """Read live values for the given resource ids (one request)."""
    if not ids:
        return {}
    values = controller.get_runtime_values(ids)
    if values is False or values is None:
        raise BridgeError("Could not read values from the controller")
    return {int(key): json_value(value) for key, value in values.items()}
