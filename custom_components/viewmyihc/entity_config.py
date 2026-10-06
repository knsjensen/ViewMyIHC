"""Describe and validate an entry for the built-in ``ihc`` integration's manual setup, and render it as YAML.

Pure Python (no Home Assistant imports). ViewMyIHC never creates entities itself and never writes files: it renders the
YAML entry that the user pastes into their own ``ihc:`` configuration. The fields mirror
``homeassistant/components/ihc/manual_setup.py``:

* every platform: ``id`` (required), ``name``, ``note``, ``position`` (all optional; the name defaults to ``ihc_<id>``)
* binary_sensor: ``inverting``, ``type`` (device class)
* sensor: ``unit_of_measurement``
* light: ``dimmable``, ``on_id``, ``off_id``
* switch: ``on_id``, ``off_id``

The *type* of an entity is not a field: it is the list (``switch:``, ``light:`` …) the entry is placed in.
"""

from __future__ import annotations

import json
from typing import Any

PLATFORMS = ("binary_sensor", "light", "sensor", "switch")

# options per platform, in the order they are written
PLATFORM_OPTIONS: dict[str, tuple[str, ...]] = {
    "binary_sensor": ("inverting", "type"),
    "light": ("dimmable", "on_id", "off_id"),
    "sensor": ("unit_of_measurement",),
    "switch": ("on_id", "off_id"),
}
_BOOLEAN_OPTIONS = frozenset({"inverting", "dimmable"})
_ID_OPTIONS = frozenset({"on_id", "off_id"})

_NAME_MAX = 120
_TEXT_MAX = 500

# resource value kinds the built-in integration cannot represent
_UNSUPPORTED_KINDS = {"time", "timer", "timertime", "enum", "weekday", "date"}
_UNSUPPORTED_REASON = (
    "Den indbyggede IHC-integration har endnu ingen entitetstype til tid, timer, valg, ugedag eller dato."
)

LABELS = {"binary_sensor": "Binær sensor", "light": "Lys", "sensor": "Sensor", "switch": "Kontakt"}


def _option(platform: str, available: bool = True, reason: str = "") -> dict[str, Any]:
    return {"platform": platform, "label": LABELS[platform], "available": available, "reason": reason}


def suggest(detail: dict[str, Any]) -> dict[str, Any]:
    """Propose which list a project resource belongs in, and defaults for the form.

    ``detail`` is the dict from ``Project.detail()``. The result is only a suggestion.
    """
    kind = detail.get("kind")
    is_input = detail.get("tag", "").endswith("input")

    if kind in _UNSUPPORTED_KINDS:
        options = [_option(p, False, _UNSUPPORTED_REASON) for p in PLATFORMS]
        default = None
    else:
        options = [_option(p) for p in PLATFORMS]
        if kind == "temperature":
            default = "sensor"
            for opt in options:
                if opt["platform"] in ("binary_sensor", "switch"):
                    opt["available"], opt["reason"] = False, "En temperatur er et tal og passer kun som sensor."
        elif kind == "integer":
            default = "sensor"
        elif kind == "bool" and is_input:
            default = "binary_sensor"
        else:
            default = "switch"
        if kind == "bool":
            for opt in options:
                if opt["platform"] == "sensor":
                    opt["available"], opt["reason"] = False, "En sensor i IHC-integrationen læser et tal (kommatal)."

    names = [p["name"] for p in detail.get("path", [])]
    parent = names[-2] if len(names) >= 2 else ""
    node = detail.get("name", "")
    candidates: list[str] = []
    for text in (node, f"{parent} {node}".strip() if parent else "", " – ".join(names[1:]) if len(names) > 2 else ""):
        if text and text not in candidates:
            candidates.append(text)

    return {
        "id": detail["id"],
        "kind": kind,
        "default_platform": default,
        "platforms": options,
        "name_suggestions": candidates,
        "defaults": {
            "name": candidates[1] if len(candidates) > 1 and len(node) < 12 else node,
            "note": detail.get("note", "") or "",
            "position": names[0] if names else "",
        },
        "option_defaults": {"unit_of_measurement": "°C" if kind == "temperature" else ""},
        "supported": default is not None,
    }


class EntityConfigError(ValueError):
    """Validation failed; ``errors`` maps field -> message."""

    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))
        self.errors = errors


def _text(value: Any, limit: int) -> str:
    return str(value or "").replace("\r\n", "\n").strip()[:limit]


def _positive_int(value: Any, field: str, errors: dict[str, str], *, required: bool = False) -> int | None:
    if value in (None, "", 0, "0"):
        if required:
            errors[field] = "Skal angives"
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        errors[field] = "Skal være et heltal"
        return None
    if number <= 0:
        errors[field] = "Skal være et positivt heltal"
        return None
    return number


def validate_entry(raw: dict[str, Any], device_classes: set[str] | None = None) -> dict[str, Any]:
    """Return a clean entry or raise :class:`EntityConfigError`."""
    errors: dict[str, str] = {}
    platform = raw.get("platform")
    if platform not in PLATFORMS:
        errors["platform"] = "Ukendt entitetstype"
    ihc_id = _positive_int(raw.get("id"), "id", errors, required=True)
    entry: dict[str, Any] = {
        "platform": platform,
        "id": ihc_id,
        "name": _text(raw.get("name"), _NAME_MAX),
        "note": _text(raw.get("note"), _TEXT_MAX),
        "position": _text(raw.get("position"), _NAME_MAX),
        "options": {},
    }
    options_in = raw.get("options") or {}
    if platform in PLATFORMS:
        opts: dict[str, Any] = {}
        for key in PLATFORM_OPTIONS[platform]:
            value = options_in.get(key)
            if key in _BOOLEAN_OPTIONS:
                opts[key] = bool(value)
            elif key in _ID_OPTIONS:
                number = _positive_int(value, f"options.{key}", errors)
                if number:
                    opts[key] = number
            elif key == "type":
                device_class = _text(value, 40)
                if device_class and device_classes is not None and device_class not in device_classes:
                    errors["options.type"] = "Ukendt sensortype"
                elif device_class:
                    opts[key] = device_class
            else:
                text = _text(value, 30)
                if text:
                    opts[key] = text
        entry["options"] = opts
    if errors:
        raise EntityConfigError(errors)
    return entry


def _scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    # JSON strings are valid YAML double-quoted scalars (quotes, newlines and unicode are handled)
    return json.dumps(str(value), ensure_ascii=False)


def entry_fields(entry: dict[str, Any]) -> list[tuple[str, Any]]:
    """The ``(key, value)`` pairs written for an entry. Only values that differ from the integration's defaults."""
    fields: list[tuple[str, Any]] = [("id", entry["id"])]
    for key in ("name", "note", "position"):
        if entry.get(key):
            fields.append((key, entry[key]))
    for key in PLATFORM_OPTIONS[entry["platform"]]:
        value = entry.get("options", {}).get(key)
        if value:  # False / 0 / "" are the defaults
            fields.append((key, value))
    return fields


def render_entry(entry: dict[str, Any], indent: int = 0) -> str:
    """The YAML list item for an entry, indented by ``indent`` spaces (the ``-`` sits at that column)."""
    pad = " " * indent
    lines = []
    for index, (key, value) in enumerate(entry_fields(entry)):
        lines.append(f"{pad}{'- ' if index == 0 else '  '}{key}: {_scalar(value)}")
    return "\n".join(lines)
