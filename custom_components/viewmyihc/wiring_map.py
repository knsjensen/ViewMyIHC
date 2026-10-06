"""What the wiring map draws: modules per dataline with their terminals, and the products wired to them (pure Python).

Everything comes from the project: the module on each line (as entered in IHC Visual), the address of each dataline
resource (which line and terminal it is wired to) and the product it belongs to. Wireless (airlink) products have
no terminals; they are listed per product with their channels.
"""

from __future__ import annotations

from typing import Any

from .dataline_layout import layout
from .project_parser import ROOT_ID, Project


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
    }


def wiring(project: Project) -> dict[str, Any]:
    lines = layout(project)
    products: dict[int, dict[str, Any]] = {}
    for side in ("inputs", "outputs"):
        for line in lines[side]:
            for slot in line["slots"]:
                if "name" in slot and slot.get("product_id") in project.nodes:
                    products.setdefault(slot["product_id"], _product(project, slot["product_id"]))
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
