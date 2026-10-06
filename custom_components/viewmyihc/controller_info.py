"""Read-only diagnostics from the controller: the user log, sent notifications, the e-mail control log and the
dataline address space. Blocking calls (run them in the executor); secrets are removed like on the admin pages.
"""

from __future__ import annotations

import base64
from typing import Any

from .admin_reader import _body_payload, _local
from .ihc_bridge import BridgeError, soap_action

LANGUAGES = ("da", "en")


def _as_list(payload: Any) -> list[Any]:
    if payload is None:
        return []
    return payload if isinstance(payload, list) else [payload]


def user_log(controller: Any, language: str = "da") -> list[str]:
    """The controller's own log (what IHC Administrator shows), one entry per line, as the controller wrote it."""
    body = (
        '<getUserLog1 xmlns="utcs" /><getUserLog2 xmlns="utcs">0</getUserLog2>'
        f'<getUserLog3 xmlns="utcs">{language if language in LANGUAGES else "da"}</getUserLog3>'
    )
    document = soap_action(controller, "/ws/ConfigurationService", "getUserLog", body)
    data = next((e.text for e in document.iter() if _local(e.tag) == "data"), None)
    if not data:
        return []
    try:
        text = base64.b64decode(data).decode("utf-8", errors="replace")
    except ValueError as err:
        raise BridgeError(f"The user log could not be decoded: {err}") from err
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def notifications(controller: Any) -> list[dict[str, Any]]:
    """SMS and e-mail messages the controller has sent (or tried to send)."""
    return _as_list(_body_payload(soap_action(controller, "/ws/NotificationManagerService", "getMessages")))


def control_log(controller: Any) -> list[dict[str, Any]]:
    """Commands the controller received by e-mail/SMS (message control)."""
    return _as_list(_body_payload(soap_action(controller, "/ws/MessageControlLogService", "getEvents")))


def control_enabled(controller: Any) -> bool:
    """Whether e-mail/SMS control is on; when it is off the controller keeps no control log (and refuses to give one)."""
    return _body_payload(soap_action(controller, "/ws/ConfigurationService", "getEmailControlEnabled")) == "true"


# the clear buttons of IHC Administrator (all without parameters)
CLEAR = {
    "userlog": ("/ws/ConfigurationService", "clearUserLog"),
    "messages": ("/ws/NotificationManagerService", "clearMessages"),
    "control": ("/ws/MessageControlLogService", "emptyLog"),
}


def clear(controller: Any, what: str) -> None:
    service, operation = CLEAR[what]
    soap_action(controller, service, operation)


def dataline(controller: Any) -> dict[str, list[dict[str, int]]]:
    """Every dataline input and output address the controller knows, with its resource id."""
    result: dict[str, list[dict[str, int]]] = {}
    for key, operations in (("inputs", ("getAllDatalineInputs", "getExtraDatalineInputs")),
                            ("outputs", ("getAllDatalineOutputs", "getExtraDatalineOutputs"))):
        seen: dict[int, dict[str, int]] = {}
        for operation in operations:
            for item in _as_list(_body_payload(soap_action(controller, "/ws/ResourceInteractionService", operation))):
                try:
                    entry = {"address": int(item["datalineNumber"]), "id": int(item["resourceID"]),
                             "extra": operation.startswith("getExtra")}
                except (KeyError, TypeError, ValueError):
                    continue
                seen.setdefault(entry["id"], entry)
        result[key] = sorted(seen.values(), key=lambda e: (e["extra"], e["address"]))
    return result
