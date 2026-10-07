"""What the wiring map draws: modules per dataline with their terminals, and the products wired to them (pure Python).

Everything comes from the project: the module on each line (as entered in IHC Visual), the address of each dataline
resource (which line and terminal it is wired to) and the product it belongs to. Wireless (airlink) products have
no terminals; they are listed per product with their channels.
"""

from __future__ import annotations

import re
from typing import Any

from .dataline_layout import layout
from .project_parser import ROOT_ID, Project


# the controller's dataline connectors: 8 input lines of 16 addresses, 16 output lines of 8 (128 + 128)
LINES = {"inputs": 8, "outputs": 16}

# the wire colours people write in IHC Visual's "Ledningsfarve" (free text, Danish and English)
COLOURS = {
    "sort": "#1f1f1f", "black": "#1f1f1f", "hvid": "#f4f4f4", "white": "#f4f4f4", "grå": "#8c8c8c", "gra": "#8c8c8c",
    "grey": "#8c8c8c", "gray": "#8c8c8c", "brun": "#8b5a2b", "brown": "#8b5a2b", "rød": "#d32f2f", "red": "#d32f2f",
    "orange": "#f57c00", "gul": "#fbc02d", "yellow": "#fbc02d", "grøn": "#388e3c", "green": "#388e3c",
    "blå": "#1976d2", "blue": "#1976d2", "lilla": "#8e24aa", "violet": "#7b1fa2", "purple": "#8e24aa",
    "pink": "#ec407a", "lyserød": "#ec407a", "turkis": "#00acc1", "turquoise": "#00acc1",
}


def wire_colours(text: str) -> list[str]:
    """The colours of a wire, in order: "Grøn (0V = Sort)" is green, "Orange+Grøn" and "K1: Violet, K2: Hvid" two."""
    found: list[str] = []
    for word in re.findall(r"[^\W\d_]+", re.sub(r"\([^)]*\)?", " ", text or "").lower()):
        colour = COLOURS.get(word)
        if colour and colour not in found:
            found.append(colour)
    return found


def _location(project: Project, node_id: int) -> str:
    node = project.nodes.get(node_id)
    current = project.nodes.get(node.parent) if node is not None else None
    while current is not None and current.id != ROOT_ID and current.category != "group":
        current = project.nodes.get(current.parent)
    return current.name if current is not None and current.id != ROOT_ID else ""


def _product(project: Project, product_id: int) -> dict[str, Any]:
    node = project.nodes[product_id]
    return {
        "id": node.id, "name": node.name, "identifier": node.attrs.get("product_identifier", ""), "kind": node.tag,
        "location": _location(project, node.id), "position": node.attrs.get("position", ""),
        "cable_type": node.attrs.get("cabletype", ""), "cable_number": node.attrs.get("cablenumber", ""),
    }


def wiring(project: Project) -> dict[str, Any]:
    lines = layout(project)
    products: dict[int, dict[str, Any]] = {}
    for side in ("inputs", "outputs"):
        for line in lines[side]:
            for slot in line["slots"]:
                if "name" in slot and slot.get("product_id") in project.nodes:
                    products.setdefault(slot["product_id"], _product(project, slot["product_id"]))
                    colour = project.nodes[slot["id"]].attrs.get("cable_colour", "")
                    slot["colour"], slot["colours"] = colour, wire_colours(colour)
        # every connector of the controller, the free ones too
        present = {line["line"] for line in lines[side]}
        lines[side] = sorted(lines[side] + [
            {"line": n, "type": None, "location": "", "capacity": 0, "used": 0, "outside": 0, "slots": [], "free": True}
            for n in range(1, LINES[side] + 1) if n not in present], key=lambda line: line["line"])
    airlink: dict[str, list[dict[str, Any]]] = {"inputs": [], "outputs": []}
    unwired = []
    for node in project.nodes.values():
        if node.tag == "product_airlink":
            for child in (project.nodes[c] for c in node.children):
                if child.tag in ("airlink_input", "airlink_output"):
                    side = "inputs" if child.tag == "airlink_input" else "outputs"
                    airlink[side].append({"id": child.id, "name": child.name, "kind": child.value_kind, "product_id": node.id,
                                          "channel": child.attrs.get("address_channel", ""), "links": len(child.links)})
                    products.setdefault(node.id, _product(project, node.id))
        elif node.tag == "product_dataline" and node.id not in products:
            unwired.append(_product(project, node.id))  # no dataline address (e.g. temperature sensors)
    return {"inputs": lines["inputs"], "outputs": lines["outputs"], "airlink": airlink,
            "products": sorted(products.values(), key=lambda p: p["id"]), "unwired": unwired}
