"""Lay the dataline addresses out per line and module (pure Python).

An IHC controller has input lines of 16 addresses and output lines of 8 (input line n = addresses 16(n-1)+1 … 16n,
output line n = 8(n-1)+1 … 8n). The module on each line is entered in IHC Visual (``dataline_input_module`` with
``module_type`` and ``location``), and decides how many of the line's addresses physically exist: a 230 V input
module has 8 inputs although its line has 16 addresses.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .project_parser import Project, parse_id

LINE_SIZE = {"inputs": 16, "outputs": 8}
_TAG = {"inputs": "dataline_input", "outputs": "dataline_output"}

# usable positions per module type (types not listed get the whole line)
MODULE_SLOTS = {
    "Input 230": 8,
    "Input 24": 16,
    "Input 24/3": 16,
    "Output 230/10": 8,
    "Output 24": 8,
}


def _project_addresses(project: Project, key: str) -> dict[int, int]:
    """``{address: resource id}`` for the project's dataline resources of one kind (address 0 = not connected)."""
    found: dict[int, int] = {}
    for node in project.nodes.values():
        if node.tag != _TAG[key] or not node.attrs.get("address_dataline"):
            continue
        try:
            address = parse_id(node.attrs["address_dataline"])
        except ValueError:
            continue
        if address > 0:
            found.setdefault(address, node.id)
    return found


def _offset(project_ids: dict[int, int], controller: list[dict[str, Any]]) -> int:
    """How the controller's ``datalineNumber`` relates to the project's address (expected 0; learned, not assumed)."""
    address_of = {rid: address for address, rid in project_ids.items()}
    deltas = Counter(address_of[e["id"]] - e["address"] for e in controller if e["id"] in address_of)
    return deltas.most_common(1)[0][0] if deltas else 0


def _describe(project: Project, resource_id: int) -> dict[str, Any]:
    node = project.nodes[resource_id]
    path = project.path(node.id)
    return {"id": node.id, "name": node.name, "label": project.label(node.id), "kind": node.value_kind,
            "product": path[-2]["name"] if len(path) > 1 else None, "product_id": node.parent, "links": len(node.links)}


def layout(project: Project, controller: dict[str, list[dict[str, Any]]] | None = None) -> dict[str, Any]:
    """``{"inputs": [line], "outputs": [line]}``; each line lists its usable slots plus any used address outside them."""
    result: dict[str, Any] = {}
    for key, size in LINE_SIZE.items():
        used = _project_addresses(project, key)
        entries = [e for e in (controller or {}).get(key, []) if not e.get("extra")]
        shift = _offset(used, entries)
        controller_ids = {e["address"] + shift: e["id"] for e in entries}
        modules = project.modules.get(key, {})
        line_numbers = sorted(set(modules) | {(a - 1) // size + 1 for a in used})
        lines = []
        for number in line_numbers:
            module = modules.get(number)
            capacity = MODULE_SLOTS.get(module["type"], size) if module else size
            slots = []
            for position in range(1, size + 1):
                address = (number - 1) * size + position
                usable = position <= capacity
                if not usable and address not in used:
                    continue
                slot: dict[str, Any] = {"address": address, "position": position, "usable": usable}
                if address in used:
                    slot.update(_describe(project, used[address]))
                elif address in controller_ids:
                    slot["id"] = controller_ids[address]
                slots.append(slot)
            lines.append({
                "line": number, "type": module["type"] if module else None, "location": module["location"] if module else "",
                "capacity": capacity, "used": sum(1 for s in slots if "name" in s),
                "outside": sum(1 for s in slots if "name" in s and not s["usable"]), "slots": slots,
            })
        result[key] = lines
    return result
