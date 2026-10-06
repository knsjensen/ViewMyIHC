"""Read-only access to the settings that the IHC Administrator program shows.

The operation names come from the SOAP service classes in the controller's own ``clients.jar``
(``com.schneider.utcs.webservice.*``). Responses are converted to plain nested dicts so the panel can
show them without knowing every field; secrets are always removed before leaving this module.
"""

from __future__ import annotations

import logging
import re
from typing import Any
import xml.etree.ElementTree as ET

from .ihc_bridge import BridgeError, soap_action

_LOGGER = logging.getLogger(__name__)

# key, title, service, operation
SECTIONS: tuple[tuple[str, str, str, str], ...] = (
    ("system", "System", "/ws/ConfigurationService", "getSystemInfo"),
    ("time", "Tid og sommertid", "/ws/TimeManagerService", "getSettings"),
    ("local_time", "Lokal tid", "/ws/TimeManagerService", "getCurrentLocalTime"),
    ("uptime", "Oppetid", "/ws/TimeManagerService", "getUptime"),
    ("users", "Brugere", "/ws/UserManagerService", "getUsers"),
    ("network", "Netværk", "/ws/ConfigurationService", "getNetworkSettings"),
    ("dns", "DNS", "/ws/ConfigurationService", "getDNSServers"),
    ("web_access", "Webadgang", "/ws/ConfigurationService", "getWebAccessControl"),
    ("smtp", "E-mail (SMTP)", "/ws/ConfigurationService", "getSMTPSettings"),
    ("email_control", "E-mail kontrol", "/ws/ConfigurationService", "getEmailControlSettings"),
    ("sms_modem", "SMS-modem", "/ws/SMSModemService", "getSMSModemSettings"),
    ("sms_status", "SMS-modem: status", "/ws/SMSModemService", "getSMSModemStatus"),
    ("sms_info", "SMS-modem: enhed", "/ws/SMSModemService", "getSMSModemInfo"),
)

_SECRET = re.compile(r"(pass|pwd|secret|pincode|^pin$|token|^key$)", re.IGNORECASE)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def element_to_py(element: ET.Element) -> Any:
    """Convert a SOAP response element into dict/list/str, dropping secrets."""
    children = list(element)
    if not children:
        text = (element.text or "").strip()
        return text if text != "" else None
    result: dict[str, Any] = {}
    for child in children:
        key = _local(child.tag)
        value = "***" if _SECRET.search(key) else element_to_py(child)
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value
    return result


def _body_payload(document: ET.Element) -> Any:
    body = next((child for child in document.iter() if _local(child.tag) == "Body"), None)
    if body is None or len(body) == 0:
        return None
    payload = element_to_py(body[0])
    # unwrap the single wrapper element IHC puts around results (e.g. getUsers2)
    if isinstance(payload, dict) and len(payload) == 1:
        return next(iter(payload.values()))
    return payload


def read_admin(controller: Any, keys: set[str] | None = None) -> list[dict[str, Any]]:
    """Run the read-only admin queries (all, or only the sections in ``keys``).

    Returns ``[{key, title, data | error}]``. The controller offers no "changed since" marker for these
    settings (only the project has a revision), so callers cache the result instead of re-reading it.
    """
    sections: list[dict[str, Any]] = []
    for key, title, service, operation in SECTIONS:
        if keys is not None and key not in keys:
            continue
        entry: dict[str, Any] = {"key": key, "title": title, "operation": operation}
        try:
            entry["data"] = _body_payload(soap_action(controller, service, operation))
            if key == "email_control" and isinstance(entry["data"], dict):
                enabled = _body_payload(soap_action(controller, service, "getEmailControlEnabled"))
                entry["data"] = {"enabled": enabled, **entry["data"]}
        except BridgeError as err:
            entry["error"] = str(err)
        except Exception as err:  # noqa: BLE001 - one broken section must not hide the others
            _LOGGER.debug("Admin section %s failed", key, exc_info=True)
            entry["error"] = f"{type(err).__name__}: {err}"
        sections.append(entry)
    return sections
