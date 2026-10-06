"""Read the SceneDesign project: who gets SMS/e-mail messages on which resource, and who may control the controller.

IHC SceneDesign keeps its own project on the controller, separate from the IHC Visual project. It is a ZIP file
(``.icz``) fetched in segments through ``ModuleService``; inside, ``project.icw`` (UTF-8 XML) holds the scenes for
SceneView and four lists the controller acts on:

* ``notifications`` / ``smsnotifications`` – a message when a resource goes on (``inactive_to_active``) or off;
* ``emailcontrols`` / ``smscontrols`` – a trigger text in an incoming e-mail/SMS switches a resource on, off or pulses it.

SMS recipients and accepted SMS senders are not phone numbers but a mask of 30 ``0``/``1`` characters, one per phone
number slot of the SMS modem (those numbers are in the IHC project). Read-only: nothing here writes to the controller.
"""

from __future__ import annotations

import base64
import io
import math
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

from .admin_reader import _body_payload, _local
from .ihc_bridge import BridgeError, soap_action

try:  # defusedxml is a requirement of the built-in ihc integration
    from defusedxml import ElementTree as SafeET
except ImportError:  # pragma: no cover - only outside Home Assistant
    SafeET = ET

MODULE = "/ws/ModuleService"
SMS_SLOTS = 30
MAX_SEGMENTS = 400


class SceneProjectError(Exception):
    """The scene project could not be read."""


def project_info(controller: Any) -> dict[str, Any]:
    info = _body_payload(soap_action(controller, MODULE, "getSceneProjectInfo"))
    return info if isinstance(info, dict) else {}


def _file_name(info: dict[str, Any]) -> str:
    """The name SceneDesign asks for: the file name of ``filepath`` without ``.icz`` (else ``name``)."""
    path = str(info.get("filepath") or "").replace("\\", "/").rsplit("/", 1)[-1]
    if path.lower().endswith(".icz"):
        path = path[:-4]
    return path or str(info.get("name") or "")


def download(controller: Any, info: dict[str, Any] | None = None) -> bytes:
    """The ``.icz`` file, segment by segment like SceneDesign (blocking)."""
    info = info if info is not None else project_info(controller)
    name = _file_name(info)
    if not name:
        raise SceneProjectError("The controller has no scene project")
    try:
        size = int(info.get("size") or 0)
        segment = int(_body_payload(soap_action(controller, MODULE, "getSceneProjectSegmentationSize")) or 0)
        count = math.ceil(size / segment) if size and segment else MAX_SEGMENTS
    except (TypeError, ValueError):
        count = MAX_SEGMENTS
    chunks: list[bytes] = []
    for index in range(min(count, MAX_SEGMENTS)):
        body = (f'<getSceneProjectSegment1 xmlns="utcs">{_escape(name)}</getSceneProjectSegment1>'
                f'<getSceneProjectSegment2 xmlns="utcs">{index}</getSceneProjectSegment2>')
        document = soap_action(controller, MODULE, "getSceneProjectSegment", body)
        data = next((e.text for e in document.iter() if _local(e.tag) == "data"), None)
        if not data:
            break
        chunks.append(base64.b64decode(data))
    if not chunks:
        raise SceneProjectError("The controller returned an empty scene project")
    return b"".join(chunks)


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _rid(element: ET.Element | None) -> int | None:
    resource = element.find("resource") if element is not None else None
    raw = (resource.get("rid") if resource is not None else "") or ""
    raw = raw.split("x", 1)[-1] if "x" in raw.lower() else raw
    try:
        return int(raw, 16)
    except ValueError:
        return None


def _slots(mask: str | None) -> list[int]:
    mask = (mask or "").strip()
    if mask and set(mask) <= {"0", "1"}:
        return [i + 1 for i, bit in enumerate(mask[:SMS_SLOTS]) if bit == "1"]
    return []


def _text(element: ET.Element | None, path: str) -> str:
    found = element.find(path) if element is not None else None
    return (found.text or "").strip() if found is not None else ""


def _key(value: str | None) -> str:
    """``text.emailcontrol.off_to_on_action`` -> ``off_to_on_action`` (the panel translates it)."""
    return (value or "").rsplit(".", 1)[-1]


def parse(icz: bytes) -> dict[str, Any]:
    """The four message lists from an ``.icz`` file."""
    try:
        with zipfile.ZipFile(io.BytesIO(icz)) as archive:
            name = next((n for n in archive.namelist() if n.lower().endswith(".icw")), None)
            if name is None:
                raise SceneProjectError("No project.icw in the scene project")
            root = SafeET.fromstring(archive.read(name))
    except (zipfile.BadZipFile, ET.ParseError, ValueError) as err:
        raise SceneProjectError(f"The scene project cannot be read: {err}") from err
    if root.tag != "icwproject":
        raise SceneProjectError(f"Not a SceneDesign project (<{root.tag}>)")

    def notification(item: ET.Element, sms: bool, index: int) -> dict[str, Any]:
        message = item.find("message")
        recipient = message.get("recipient", "") if message is not None else ""
        return {
            "key": f"{'smsnotifications' if sms else 'notifications'}:{index}", "channel": "sms" if sms else "email", "resource": _rid(item), "event": _key(item.get("event")),
            "recipients": [] if sms else [r.strip() for r in recipient.split(";") if r.strip()],
            "slots": _slots(recipient) if sms else [],
            "subject": _text(message, "subject"), "body": _text(message, "body"),
        }

    def control(item: ET.Element, sms: bool, index: int) -> dict[str, Any]:
        auth = item.find("authorization")
        action = item.find("action")
        sender = _text(auth, "acceptsenderaddress")
        return {
            "key": f"{'smscontrols' if sms else 'emailcontrols'}:{index}", "channel": "sms" if sms else "email", "resource": _rid(item),
            "action": _key(action.get("type") if action is not None else ""),
            "authorization": _key(auth.get("type") if auth is not None else ""),
            "trigger": _text(auth, "triggersubject"),
            "senders": _slots(sender) if sms else ([sender] if sender else []),
            "confirmation_address": _text(auth, "confirmationaddress"),
            "confirmation": _text(item, "executionconfirmation/body"),
            "confirmation_message": _text(auth, "confirmationmessage"),
        }

    return {
        "name": root.get("name", ""), "version": root.get("version", ""), "description": _text(root, "description"),
        "notifications": [notification(e, False, i) for i, e in enumerate(root.iterfind("notifications/notification"))]
        + [notification(e, True, i) for i, e in enumerate(root.iterfind("smsnotifications/smsnotification"))],
        "controls": [control(e, False, i) for i, e in enumerate(root.iterfind("emailcontrols/emailcontrol"))]
        + [control(e, True, i) for i, e in enumerate(root.iterfind("smscontrols/smscontrol"))],
        "scenes": len(root.findall("scenes/scene")),
    }


def read(controller: Any, cached: dict[str, Any] | None) -> dict[str, Any]:
    """Info + parsed lists; downloads again only when the controller's checksum (``crc``) changed (blocking)."""
    info = project_info(controller)
    if not info:
        raise BridgeError("The controller has no scene project")
    crc = str(info.get("crc") or "")
    if cached is not None and crc and cached.get("crc") == crc:
        return cached
    icz = download(controller, info)
    # "icz": the file itself, only on a fresh download, so the caller can keep a copy (it is not cached)
    return {"crc": crc, "info": {k: info.get(k) for k in ("name", "description", "version", "lastmodified", "size")},
            **parse(icz), "icz": icz}
