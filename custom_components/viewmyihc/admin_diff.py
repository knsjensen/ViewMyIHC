"""Compare two reads of the controller's admin settings.

Pure Python (no Home Assistant imports). The controller has no "settings changed" marker, so the panel shows
the last saved state at once, reads the controller in the background and uses this module to find out what
(if anything) differs.

A *path* addresses one value inside a section as a list of segments: dictionary keys, and ``[<id>]`` for list
items, where ``<id>`` is the ``username`` for users (so reordering does not look like a change) or the index.
The frontend builds the very same paths while rendering, to mark changed values.
"""

from __future__ import annotations

from typing import Any

# whole sections / values that change all the time and must never be reported as a "change"; a volatile key
# anywhere in a path covers everything below it (timeAndDateInUTC is the running clock in the time settings)
VOLATILE_SECTIONS = frozenset({"local_time", "uptime", "sms_status"})  # sms_status: coverage, operator
VOLATILE_KEYS = frozenset({"uptime", "realtimeclock", "timeAndDateInUTC"})


def item_id(item: Any, index: int) -> str:
    """How a list item is identified in a path."""
    if isinstance(item, dict) and item.get("username"):
        return str(item["username"])
    return str(index)


def flatten(value: Any, path: tuple[str, ...] = ()) -> dict[tuple[str, ...], Any]:
    """``{path: scalar}`` for every leaf of a nested dict/list structure."""
    if isinstance(value, dict):
        result: dict[tuple[str, ...], Any] = {}
        for key, item in value.items():
            result.update(flatten(item, (*path, str(key))))
        return result
    if isinstance(value, list):
        result = {}
        for index, item in enumerate(value):
            result.update(flatten(item, (*path, f"[{item_id(item, index)}]")))
        return result
    return {path: value}


def diff_section(key: str, old: Any, new: Any) -> list[dict[str, Any]]:
    """Changes between two reads of one section (volatile data is ignored)."""
    if key in VOLATILE_SECTIONS:
        return []
    before, after = flatten(old), flatten(new)
    changes: list[dict[str, Any]] = []
    for path in sorted(set(before) | set(after)):
        if VOLATILE_KEYS.intersection(path):
            continue
        if path not in after:
            changes.append({"type": "removed", "path": list(path), "old": before[path], "new": None})
        elif path not in before:
            changes.append({"type": "added", "path": list(path), "old": None, "new": after[path]})
        elif before[path] != after[path]:
            changes.append({"type": "changed", "path": list(path), "old": before[path], "new": after[path]})
    return changes


def merge_refresh(
    saved: dict[str, dict[str, Any]], fresh: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Combine a fresh read with the saved state.

    ``saved`` is ``{section key: section}``; ``fresh`` the sections just read (each with ``data`` or ``error``).

    Returns ``(sections to show, sections to save, changes)``. A section that could not be read keeps its last
    good data (shown with ``error`` and ``stale``), so one failing call never erases what we know.
    """
    show: list[dict[str, Any]] = []
    keep: dict[str, dict[str, Any]] = {}
    changes: list[dict[str, Any]] = []
    for section in fresh:
        key = section["key"]
        previous = saved.get(key)
        if "error" in section:
            if previous is not None and "data" in previous:
                show.append({**previous, "error": section["error"], "stale": True})
                keep[key] = previous
            else:
                show.append(section)
            continue
        if previous is not None and "data" in previous:
            changes.extend({**change, "section": key} for change in diff_section(key, previous["data"], section["data"]))
        show.append(section)
        keep[key] = section
    return show, keep, changes
