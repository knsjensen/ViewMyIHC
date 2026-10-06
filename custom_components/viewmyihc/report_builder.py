"""The content of the documentation reports IHC Visual / the controller's report pages make (pure Python).

Three reports, as on the controller's own report page (``/reports/LK_da/entry_page.html``):

* installation documentation – dataline inputs and outputs with cable data, the modules per line, and each product;
* function documentation – for the residents: per location, what each button of the marked products does (the
  note of the function block input it is linked to);
* function block documentation – each function block with its inputs, outputs and settings, initial values and links.

Only data is built here; the panel lays it out for the screen and for printing.
"""

from __future__ import annotations

from typing import Any

from .project_parser import ROOT_ID, Node, Project, parse_id

LINE_SIZE = {"dataline_input": 16, "dataline_output": 8}


def terminal(address: int, divider: int) -> str:
    """IHC's own terminal numbering, like the module labels: line.01–.08, then .11–.18 (``?`` if not connected)."""
    if address <= 0:
        return "?"
    bit = (address - 1) % divider
    return f"{(address - 1) // divider + 1}.{bit + 3 if bit > 7 else f'0{bit + 1}'}"


def _address(node: Node) -> int:
    try:
        return parse_id(node.attrs.get("address_dataline", "0") or "0")
    except ValueError:
        return 0


def _note(node: Node) -> str:
    return node.attrs.get("note") or next((v for k, v in node.attrs.items() if k.startswith("note") and v), "")


def _parent(project: Project, node: Node) -> Node | None:
    return project.nodes.get(node.parent)


def _group_name(project: Project, node: Node) -> str:
    """The location (group) a product or function block sits in."""
    current = _parent(project, node)
    while current is not None and current.id != ROOT_ID and current.category != "group":
        current = _parent(project, current)
    return current.name if current is not None and current.id != ROOT_ID else ""


def initial_value(project: Project, node: Node) -> str:
    """The initial value as IHC Visual shows it."""
    a, tag = node.attrs, node.tag
    if tag in ("resource_time",):
        return ":".join(f"{int(a.get(k, 0) or 0):02d}" for k in ("hour", "minute", "second"))
    if tag in ("resource_timer", "resource_timertime"):
        base = ":".join(f"{int(a.get(k, 0) or 0):02d}" for k in ("hour", "minute", "second"))
        ms = int(a.get("millisecond", 0) or 0)
        return f"{base},{ms:03d}" if ms else base
    if tag == "resource_date":
        return f"{a.get('day', '?')}.{a.get('month', '?')}.{a.get('year', '?')}"
    value = a.get("inivalue", "")
    if not value:
        return ""
    if tag == "resource_enum":
        try:
            return project.enum_values.get(parse_id(value), {}).get("name", value)
        except ValueError:
            return value
    if tag == "resource_temperature":
        return f"{value} °C"
    if tag == "resource_light_level":
        return f"{value} %"
    return value


# ------------------------------------------------------------------ installation documentation


def _io_row(project: Project, node: Node) -> dict[str, Any]:
    product = _parent(project, node)
    pa = product.attrs if product is not None else {}
    address = _address(node)
    return {
        "id": node.id, "address": address, "terminal": terminal(address, LINE_SIZE[node.tag]), "name": node.name,
        "note": _note(node), "product": product.name if product else "", "location": _group_name(project, product) if product else "",
        "position": pa.get("position", ""), "tag": pa.get("documentation_tag", ""), "cabletype": pa.get("cabletype", ""),
        "cablenumber": pa.get("cablenumber", ""), "power_group": pa.get("power_group", ""), "colour": node.attrs.get("cable_colour", ""),
    }


def installation(project: Project) -> dict[str, Any]:
    rows = {tag: [] for tag in LINE_SIZE}
    products = []
    for node in project.nodes.values():
        if node.tag in rows:
            rows[node.tag].append(_io_row(project, node))
        elif node.tag in ("product_dataline", "product_airlink"):
            a = node.attrs
            terminals = [
                {"direction": "in" if child.tag.endswith("input") else "out", "name": child.name,
                 "terminal": terminal(_address(child), LINE_SIZE[child.tag]) if child.tag in LINE_SIZE else "",
                 "channel": child.attrs.get("address_channel", ""), "colour": child.attrs.get("cable_colour", "")}
                for child in (project.nodes[c] for c in node.children) if child.is_resource
            ]
            serial = a.get("serialnumber", "")
            products.append({
                "id": node.id, "kind": "airlink" if node.tag == "product_airlink" else "dataline", "name": node.name,
                "location": _group_name(project, node), "position": a.get("position", ""), "tag": a.get("documentation_tag", ""),
                "cablenumber": a.get("cablenumber", ""), "cabletype": a.get("cabletype", ""), "power_group": a.get("power_group", ""),
                "serial": serial[3:].upper() if serial.startswith("_0x") else serial, "terminals": terminals,
            })
    for tag in rows:  # by address, not connected (?) last – like the controller's report
        rows[tag].sort(key=lambda r: (r["address"] <= 0, r["address"], r["name"]))
    products.sort(key=lambda p: (p["location"].lower(), p["name"].lower(), p["position"].lower()))
    modules = {key: [{"line": line, **module} for line, module in sorted(project.modules.get(key, {}).items())]
               for key in ("inputs", "outputs")}
    return {"documentation": project.documentation, "inputs": rows["dataline_input"], "outputs": rows["dataline_output"],
            "input_modules": modules["inputs"], "output_modules": modules["outputs"], "products": products}


# ------------------------------------------------------------------ function documentation (for residents)


def _does(project: Project, node: Node, product_location: str) -> list[dict[str, str]]:
    """What a button input does: the note of each function block input it is linked to."""
    result = []
    for target_id, direction in node.links:
        target = project.nodes.get(target_id)
        if target is None or direction == "scene":
            continue
        path = project.path(target.id)
        block = path[-2]["name"] if len(path) > 1 else ""
        where = _group_name(project, project.nodes[path[-2]["id"]]) if len(path) > 1 else ""
        text = _note(target) or (f"{block}: {target.name}" if block else target.name)
        result.append({"text": text, "where": "" if product_location.startswith(where) else where, "id": target.id})
    return result


def function(project: Project, only_marked: bool = True) -> dict[str, Any]:
    """Per location, the products (only those marked for the end-user report in IHC Visual, unless asked otherwise)."""
    groups: dict[int, dict[str, Any]] = {}
    marked_any = False
    for node in project.nodes.values():
        if node.tag not in ("product_dataline", "product_airlink"):
            continue
        marked = node.attrs.get("enduser_report") == "yes"
        marked_any = marked_any or marked
        if only_marked and not marked:
            continue
        location = _group_name(project, node)
        group = _parent(project, node)
        while group is not None and group.category != "group" and group.id != ROOT_ID:
            group = _parent(project, group)
        key = group.id if group is not None else ROOT_ID
        entry = groups.setdefault(key, {"id": key, "name": location, "products": []})
        children = [project.nodes[c] for c in node.children]
        entry["products"].append({
            "id": node.id, "name": node.name, "position": node.attrs.get("position", ""),
            "inputs": [{"name": c.name, "does": _does(project, c, location)} for c in children if c.tag.endswith("input")],
            "outputs": [{"name": c.name, "note": _note(c)} for c in children if c.tag.endswith("output")],
        })
    ordered = sorted(groups.values(), key=lambda g: g["name"].lower())
    for group in ordered:
        group["products"].sort(key=lambda p: (p["name"].lower(), p["position"].lower()))
    return {"documentation": project.documentation, "groups": ordered, "only_marked": only_marked, "marked_any": marked_any}


# ------------------------------------------------------------------ function block documentation

_SECTIONS = ("inputs", "outputs", "settings")


def functionblocks(project: Project) -> dict[str, Any]:
    blocks = []
    for node in project.nodes.values():
        if node.category != "functionblock" or node.hidden:
            continue
        sections = []
        for section_id in node.children:
            section = project.nodes[section_id]
            if section.tag not in _SECTIONS or section.hidden:
                continue
            resources = [
                {"id": r.id, "name": r.name, "kind": r.value_kind, "initial": initial_value(project, r), "note": _note(r),
                 "links": [{"label": project.label(t), "direction": d} for t, d in r.links if t in project.nodes and not project.nodes[t].hidden]}
                for r in (project.nodes[c] for c in section.children) if r.is_resource
            ]
            if resources:
                sections.append({"key": section.tag, "title": section.name, "resources": resources})
        blocks.append({"id": node.id, "name": node.name, "location": " / ".join(p["name"] for p in project.path(node.id)[:-1]),
                       "note": _note(node), "sections": sections})
    blocks.sort(key=lambda b: (b["location"].lower(), b["name"].lower()))
    return {"documentation": project.documentation, "blocks": blocks}


REPORTS = {"installation": installation, "function": function, "functionblocks": functionblocks}
