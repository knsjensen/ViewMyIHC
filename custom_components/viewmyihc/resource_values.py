"""Read and write single resource values in the controller's own SOAP value format.

Pure Python (no Home Assistant imports). The type of a resource is taken from what the controller reports
(``xsi:type`` of the value), never guessed from the project, so a write always uses the exact type the
controller expects. The same ``setResourceValue`` operation writes the runtime value
(``isValueRuntime=true``) or the initial value the controller starts with (``isValueRuntime=false``).
"""

from __future__ import annotations

import re
from typing import Any
from xml.etree.ElementTree import Element

XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"

BOOL, INTEGER, FLOAT, TIMER, TIME, ENUM = (
    "WSBooleanValue", "WSIntegerValue", "WSFloatingPointValue", "WSTimerValue", "WSTimeValue", "WSEnumValue",
)
EDITABLE = frozenset({BOOL, INTEGER, FLOAT, TIMER, TIME, ENUM})

_TIME = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")
_MAX_TIMER_MS = 24 * 3600 * 1000 * 100


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(element: Element, name: str) -> Element | None:
    return next((c for c in element if _local(c.tag) == name), None)


def _text(element: Element, name: str) -> str | None:
    child = _child(element, name)
    return None if child is None or child.text is None else child.text.strip()


def _number(text: str | None, kind: type) -> Any:
    if text is None or text == "":
        return None
    try:
        return kind(text)
    except ValueError:
        return None


def read_value(value: Element | None) -> dict[str, Any] | None:
    """``{type, value, editable, ...}`` for one ``<value xsi:type=...>`` element."""
    if value is None or XSI_TYPE not in value.attrib:
        return None
    ws_type = value.attrib[XSI_TYPE].split(":")[-1]
    info: dict[str, Any] = {"type": ws_type, "editable": ws_type in EDITABLE, "value": None}
    if ws_type == BOOL:
        info["value"] = _text(value, "value") == "true"
    elif ws_type in (INTEGER, FLOAT):
        kind = int if ws_type == INTEGER else float
        info["value"] = _number(_text(value, "integer" if ws_type == INTEGER else "floatingPointValue"), kind)
        info["min"] = _number(_text(value, "minimumValue"), kind)
        info["max"] = _number(_text(value, "maximumValue"), kind)
    elif ws_type == TIMER:
        info["value"] = _number(_text(value, "milliseconds"), int)
    elif ws_type == TIME:
        parts = [_number(_text(value, k), int) or 0 for k in ("hours", "minutes", "seconds")]
        info["value"] = "{:02d}:{:02d}:{:02d}".format(*parts)
    elif ws_type == ENUM:
        info["value"] = _number(_text(value, "enumValueID"), int)
        info["name"] = _text(value, "enumName")
        info["definition"] = _number(_text(value, "definitionTypeID"), int)
    else:
        info["value"] = (value.text or "").strip() or None
    return info


def read_envelope(document: Element, wrapper: str) -> dict[str, Any] | None:
    """The value inside a single-envelope answer (``getRuntimeValue2`` / ``getInitialValue2``)."""
    holder = next((e for e in document.iter() if _local(e.tag) == wrapper), None)
    if holder is None:
        return None
    return read_value(_child(holder, "value"))


def read_envelopes(document: Element, wrapper: str) -> dict[int, dict[str, Any]]:
    """``{resource id: value info}`` from a list answer (``getInitialValues2``)."""
    holder = next((e for e in document.iter() if _local(e.tag) == wrapper), None)
    result: dict[int, dict[str, Any]] = {}
    for item in [] if holder is None else list(holder):
        resource = _number(_text(item, "resourceID"), int)
        info = read_value(_child(item, "value"))
        if resource is not None and info is not None:
            result[resource] = info
    return result


def coerce(current: dict[str, Any], raw: Any, enum_ids: set[int] | None = None) -> Any:
    """Check a value from the panel against the resource's type (and limits). Raises ``ValueError``."""
    ws_type = current["type"]
    if ws_type not in EDITABLE:
        raise ValueError(f"Values of type {ws_type} cannot be changed here")
    if ws_type == BOOL:
        if not isinstance(raw, bool):
            raise ValueError("Expected on/off")
        return raw
    if ws_type in (INTEGER, FLOAT, TIMER):
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or raw != raw:
            raise ValueError("Expected a number")
        if ws_type in (INTEGER, TIMER):
            if raw != int(raw):
                raise ValueError("Expected a whole number")
            raw = int(raw)
        else:
            raw = float(raw)
        low, high = (0, _MAX_TIMER_MS) if ws_type == TIMER else (current.get("min"), current.get("max"))
        if low is not None and raw < low or high is not None and raw > high:
            raise ValueError(f"The value must be between {low} and {high}")
        return raw
    if ws_type == TIME:
        match = _TIME.match(str(raw).strip())
        if not match or int(match[1]) > 23 or int(match[2]) > 59 or int(match[3] or 0) > 59:
            raise ValueError("Expected a time (HH:MM:SS)")
        return int(match[1]), int(match[2]), int(match[3] or 0)
    # enum: the id of one of the definition's values
    if isinstance(raw, bool) or not isinstance(raw, int) or (enum_ids is not None and raw not in enum_ids):
        raise ValueError("Unknown choice")
    return raw


def set_payload(resource_id: int, current: dict[str, Any], value: Any, *, runtime: bool, enum_name: str = "") -> str:
    """Body of ``setResourceValue`` for an already coerced ``value``."""
    ws_type = current["type"]
    if ws_type == BOOL:
        fields = f"<a:value>{'true' if value else 'false'}</a:value>"
    elif ws_type == INTEGER:
        fields = f"<a:integer>{value}</a:integer>"
    elif ws_type == FLOAT:
        fields = f"<a:floatingPointValue>{value!r}</a:floatingPointValue>"
    elif ws_type == TIMER:
        fields = f"<a:milliseconds>{value}</a:milliseconds>"
    elif ws_type == TIME:
        hours, minutes, seconds = value
        fields = f"<a:hours>{hours}</a:hours><a:seconds>{seconds}</a:seconds><a:minutes>{minutes}</a:minutes>"
    elif ws_type == ENUM:
        name = enum_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        fields = (
            f"<a:definitionTypeID>{int(current['definition'])}</a:definitionTypeID>"
            f"<a:enumValueID>{value}</a:enumValueID><a:enumName>{name}</a:enumName>"
        )
    else:  # pragma: no cover - coerce() refuses these
        raise ValueError(ws_type)
    return (
        '<setResourceValue1 xmlns="utcs" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">'
        f'<value i:type="a:{ws_type}" xmlns:a="utcs.values">{fields}</value>'
        f"<typeString/><resourceID>{int(resource_id)}</resourceID>"
        f"<isValueRuntime>{'true' if runtime else 'false'}</isValueRuntime></setResourceValue1>"
    )


def accepted(document: Element) -> bool:
    """Whether the controller answered ``setResourceValue`` with ``true``."""
    holder = next((e for e in document.iter() if _local(e.tag) == "setResourceValue2"), None)
    return holder is not None and (holder.text or "").strip() == "true"
