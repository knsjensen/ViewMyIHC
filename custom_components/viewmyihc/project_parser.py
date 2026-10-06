"""Parse an IHC project (``utcs_project`` XML) into an indexed, lazily browsable tree.

Pure Python without Home Assistant imports so it can be tested and reused on its own.

Terminology used here:

* *node*      – an element of the project that is shown in the viewer
* *resource*  – a node that has a runtime value on the controller (the id is what the ``ihc``
  integration calls ``ihcid``). IDs are stored as ``_0x16837`` in the file and handled as plain
  integers (``92215``) everywhere else.
* *link*      – IHC links are pairs of ``link_to_resource`` / ``link_from_resource`` elements that
  point at each other through their ``link`` attribute. The owner (parent) of the opposite element
  is the connected resource.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
import xml.etree.ElementTree as StdET

try:  # defusedxml is a requirement of the built-in ihc integration
    from defusedxml import ElementTree as ET
except ImportError:  # pragma: no cover - only hit when running outside Home Assistant
    ET = StdET

VIEW_ALL = "all"
VIEW_INSTALLATION = "installation"
VIEW_PROGRAMS = "programs"
VIEWS = (VIEW_ALL, VIEW_INSTALLATION, VIEW_PROGRAMS)

ROOT_ID = 0

_GROUP_TAGS = {"group"}
_PRODUCT_TAGS = {"product_dataline", "product_airlink", "product_rs485_sms_modem"}
_FUNCTION_TAGS = {"functionblock"}
_SECTION_TAGS = {"inputs", "outputs", "settings", "internalsettings", "programs"}
_PROGRAM_TAGS = {"program_simple", "program_sub", "program_case"}
# A function block's internal settings and programs: nothing there is worth seeing or changing, so they and
# everything below them are kept in the index (links still resolve) but never shown
_HIDDEN_SECTIONS = {"internalsettings", "programs"}
_DATALINE_RESOURCES = {"dataline_input", "dataline_output", "airlink_input", "airlink_output"}
# Elements that carry no name of their own: their children are shown directly under the parent.
_PASS_THROUGH = {
    "actions", "action", "conditions", "condition", "events", "event", "event_power",
    "case_action", "scenes", "scene_relay", "scene_link",
}
# Elements that are never shown (and whose subtree is ignored).
_SKIPPED = {
    "link_from_resource", "link_to_resource", "enum_definitions", "customer_info", "installer_info",
    "project_info", "modified", "documentation_modules", "dataline_input_modules",
    "dataline_output_modules", "dataline_input_module", "dataline_output_module",
    "sms_modem_settings", "sms_modem_phonenumber", "sms_modem_pincode",
}
_LINK_ELEMENTS = {"link_from_resource", "link_to_resource"}
_LINK_CARRIERS = {"scene_relay", "scene_link"}

# value kind per resource tag – decides how the frontend formats the live value
_VALUE_KINDS = {
    "dataline_input": "bool", "dataline_output": "bool", "airlink_input": "bool",
    "airlink_output": "bool", "resource_input": "bool", "resource_output": "bool",
    "resource_flag": "bool", "resource_temperature": "temperature", "resource_time": "time",
    "resource_timer": "timer", "resource_timertime": "timertime", "resource_enum": "enum",
    "resource_integer": "integer", "resource_counter": "integer", "resource_weekday": "weekday",
    "resource_date": "date", "resource_scene": "scene",
}

# attributes worth showing in the detail panel, in display order
_DETAIL_ATTRS = (
    "inivalue", "hour", "minute", "second", "millisecond", "year", "month", "day", "accessibility",
    "backup", "type", "address_dataline", "address_channel", "cable_colour", "position",
    "cabletype", "cablenumber", "product_identifier", "master_name", "master_programmer",
    "locked", "documentation_tag", "power_group",
)

_XML_DECL = re.compile(r"^\s*<\?xml[^>]*\?>")


def parse_id(text: str) -> int:
    """Convert an IHC element id (``_0x16837``) to the integer used with the controller."""
    text = text.strip().lstrip("_")
    if text.lower().startswith("0x"):
        return int(text, 16)
    return int(text)


def _note(attrs: dict[str, str]) -> str:
    return attrs.get("note") or next(
        (value for key, value in attrs.items() if key.startswith("note")), ""
    )


@dataclass(slots=True)
class Node:
    """One element in the project tree."""

    id: int
    tag: str
    name: str
    category: str
    parent: int
    children: list[int] = field(default_factory=list)
    attrs: dict[str, str] = field(default_factory=dict)
    value_kind: str | None = None
    # (target resource id, direction) – direction is "to", "from" or "scene"
    links: list[tuple[int, str]] = field(default_factory=list)
    has_installation: bool = False
    has_programs: bool = False
    hidden: bool = False

    @property
    def is_resource(self) -> bool:
        return self.value_kind is not None


class ProjectError(Exception):
    """Raised when a project cannot be parsed."""


class Project:
    """An indexed IHC project."""

    def __init__(self, source: str | bytes) -> None:
        self.nodes: dict[int, Node] = {ROOT_ID: Node(ROOT_ID, "root", "", "root", ROOT_ID)}
        self.enums: dict[int, dict[str, Any]] = {}
        self.enum_values: dict[int, dict[str, Any]] = {}
        self.info: dict[str, Any] = {}
        # dataline module per line number, as entered in IHC Visual: {"inputs": {1: {"type", "location"}}, "outputs": ...}
        self.modules: dict[str, dict[int, dict[str, str]]] = {"inputs": {}, "outputs": {}}
        # project, customer and installer details from IHC Visual, only used by the reports (never in ``info``)
        self.documentation: dict[str, dict[str, str]] = {}
        # the SMS modem's 30 phone number slots (SceneDesign refers to them by slot): {slot: {"number", "label"}}
        self.sms_numbers: dict[int, dict[str, str]] = {}
        self._owner: dict[int, int] = {}  # link element id -> owning resource id
        self._pending_links: list[tuple[int, str, str]] = []  # (resource, direction, target id)
        self._parse(source)

    # ------------------------------------------------------------------ parsing

    def _parse(self, source: str | bytes) -> None:
        if isinstance(source, str):
            source = _XML_DECL.sub("", source, count=1)
        try:
            root = ET.fromstring(source)
        except (StdET.ParseError, ValueError) as err:
            raise ProjectError(f"Invalid IHC project XML: {err}") from err
        if root.tag != "utcs_project":
            raise ProjectError(f"Not an IHC project (root element is <{root.tag}>)")

        self._read_enums(root)
        self._read_modules(root)
        for settings in root.iter("sms_modem_settings"):
            for number in settings.iter("sms_modem_phonenumber"):
                try:
                    slot = int(number.get("address", ""))
                except ValueError:
                    continue
                self.sms_numbers[slot] = {"number": number.get("phonenumber", ""), "label": settings.get("name", "")}
        for tag, key in (("project_info", "project"), ("customer_info", "customer"), ("installer_info", "installer")):
            element = root.find(tag)
            if element is not None:
                self.documentation[key] = {k: v for k, v in element.attrib.items() if k != "udf"}
        for child in root:
            self._walk(child, ROOT_ID)
        self._resolve_links()
        self._flag_groups(ROOT_ID)
        project_info = root.find("project_info")
        self.info = {
            "version": f"{root.get('version_major', '?')}.{root.get('version_minor', '?')}",
            "modified": self._modified(root),
            "description": project_info.get("description", "") if project_info is not None else "",
            "nodes": len(self.nodes) - 1,
            "resources": sum(1 for n in self.nodes.values() if n.is_resource and not n.hidden),
            "functionblocks": sum(1 for n in self.nodes.values() if n.category == "functionblock"),
            "products": sum(1 for n in self.nodes.values() if n.category == "product"),
        }

    @staticmethod
    def _modified(root: StdET.Element) -> str | None:
        mod = root.find("modified")
        if mod is None:
            return None
        try:
            return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
                int(mod.get("year")), int(mod.get("month")), int(mod.get("day")),
                int(mod.get("hour")), int(mod.get("minute")),
            )
        except (TypeError, ValueError):
            return None

    def _read_modules(self, root: StdET.Element) -> None:
        for tag, key in (("dataline_input_module", "inputs"), ("dataline_output_module", "outputs")):
            for module in root.iter(tag):
                try:
                    line = int(module.get("dataline", ""))
                except ValueError:
                    continue
                self.modules[key][line] = {"type": module.get("module_type", ""), "location": module.get("location", "")}

    def _read_enums(self, root: StdET.Element) -> None:
        for definition in root.iter("enum_definition"):
            try:
                def_id = parse_id(definition.get("id", ""))
            except ValueError:
                continue
            values = []
            for value in definition.findall("enum_value"):
                try:
                    value_id = parse_id(value.get("id", ""))
                except ValueError:
                    continue
                entry = {
                    "id": value_id,
                    "name": value.get("name", ""),
                    "index": int(value.get("index", "0") or 0),
                }
                values.append(entry)
                self.enum_values[value_id] = entry
            self.enums[def_id] = {"id": def_id, "name": definition.get("name", ""), "values": values}

    def _walk(self, element: StdET.Element, parent_id: int) -> None:
        tag = element.tag
        if tag in _SKIPPED:
            return
        if tag in _PASS_THROUGH:
            if tag in _LINK_CARRIERS and element.get("link") and parent_id != ROOT_ID:
                self._pending_links.append((parent_id, "scene", element.get("link", "")))
            for child in element:
                self._walk(child, parent_id)
            return

        node = self._make_node(element, parent_id)
        if node is None:  # unknown element without an id: look inside it
            for child in element:
                self._walk(child, parent_id)
            return

        self.nodes[node.id] = node
        self.nodes[parent_id].children.append(node.id)
        for child in element:
            if child.tag in _LINK_ELEMENTS:
                self._register_link(node, child)
            else:
                self._walk(child, node.id)

    def _make_node(self, element: StdET.Element, parent_id: int) -> Node | None:
        tag = element.tag
        raw_id = element.get("id")
        if not raw_id:
            return None
        try:
            node_id = parse_id(raw_id)
        except ValueError:
            return None

        value_kind = _VALUE_KINDS.get(tag)
        if tag in _GROUP_TAGS:
            category = "group"
        elif tag in _PRODUCT_TAGS:
            category = "product"
        elif tag in _FUNCTION_TAGS:
            category = "functionblock"
        elif tag in _SECTION_TAGS:
            category = "section"
        elif tag in _PROGRAM_TAGS:
            category = "program"
        elif value_kind or tag in _DATALINE_RESOURCES or tag.startswith("resource_"):
            category = "resource"
            value_kind = value_kind or "unknown"
        else:
            return None

        attrs = {k: v for k, v in element.attrib.items() if k != "id"}
        name = attrs.pop("name", "") or {
            "programs": "Programmer", "inputs": "Input", "outputs": "Output",
            "settings": "Indstillinger", "internalsettings": "Interne indstillinger",
        }.get(tag, tag)
        hidden = tag in _HIDDEN_SECTIONS or self.nodes[parent_id].hidden
        return Node(node_id, tag, name, category, parent_id, attrs=attrs, value_kind=value_kind, hidden=hidden)

    def _register_link(self, node: Node, element: StdET.Element) -> None:
        link_id = element.get("id")
        if link_id:
            try:
                self._owner[parse_id(link_id)] = node.id
            except ValueError:
                pass
        direction = "to" if element.tag == "link_to_resource" else "from"
        if element.get("link"):
            self._pending_links.append((node.id, direction, element.get("link", "")))

    def _resolve_links(self) -> None:
        for resource_id, direction, target in self._pending_links:
            try:
                target_id = parse_id(target)
            except ValueError:
                continue
            resolved = self._owner.get(target_id)
            if resolved is None and target_id in self.nodes:
                resolved = target_id
            if resolved is None or resolved == resource_id:
                continue
            entry = (resolved, direction)
            node = self.nodes.get(resource_id)
            if node is not None and entry not in node.links:
                node.links.append(entry)

    def _flag_groups(self, node_id: int) -> tuple[bool, bool]:
        node = self.nodes[node_id]
        installation = node.category == "product"
        programs = node.category == "functionblock"
        if node.category in ("product", "functionblock"):
            return installation, programs
        for child_id in node.children:
            child_inst, child_prog = self._flag_groups(child_id)
            installation = installation or child_inst
            programs = programs or child_prog
        node.has_installation, node.has_programs = installation, programs
        return installation, programs

    # ------------------------------------------------------------------ queries

    def _visible(self, node: Node, view: str) -> bool:
        if node.hidden:
            return False
        if node.category == "group":
            # a location without any product, function block or program is noise in every view
            if view == VIEW_INSTALLATION:
                return node.has_installation
            if view == VIEW_PROGRAMS:
                return node.has_programs
            return node.has_installation or node.has_programs
        if view == VIEW_ALL:
            return True
        if view == VIEW_INSTALLATION and node.category == "functionblock":
            return False
        if view == VIEW_PROGRAMS and node.category == "product":
            return False
        return True

    def children(self, node_id: int, view: str = VIEW_ALL) -> list[dict[str, Any]]:
        """Return summaries of the visible children of ``node_id``."""
        node = self.nodes.get(node_id)
        if node is None:
            return []
        return [
            self.summary(child, view)
            for child in (self.nodes[c] for c in node.children)
            if self._visible(child, view)
        ]

    def summary(self, node: Node, view: str = VIEW_ALL) -> dict[str, Any]:
        """Compact description used for tree rows."""
        has_children = any(self._visible(self.nodes[c], view) for c in node.children)
        result: dict[str, Any] = {
            "id": node.id,
            "name": node.name,
            "tag": node.tag,
            "category": node.category,
            "has_children": has_children,
            "links": len(node.links),
        }
        if node.is_resource:
            result["kind"] = node.value_kind
        if node.category == "product" and node.attrs.get("position"):
            result["hint"] = node.attrs["position"]
        return result

    def path(self, node_id: int, *, include_sections: bool = False) -> list[dict[str, Any]]:
        """Names from the top group down to the node (sections like "Input" are left out)."""
        result: list[dict[str, Any]] = []
        current = self.nodes.get(node_id)
        while current is not None and current.id != ROOT_ID:
            if include_sections or current.category != "section":
                result.append({"id": current.id, "name": current.name})
            current = self.nodes.get(current.parent)
        result.reverse()
        return result

    def label(self, node_id: int) -> str:
        return " / ".join(p["name"] for p in self.path(node_id))

    def detail(self, node_id: int) -> dict[str, Any] | None:
        """Full description of a node for the detail panel."""
        node = self.nodes.get(node_id)
        if node is None or node.id == ROOT_ID:
            return None
        attrs = {k: node.attrs[k] for k in _DETAIL_ATTRS if k in node.attrs}
        result: dict[str, Any] = {
            "id": node.id,
            "id_hex": hex(node.id),
            "name": node.name,
            "tag": node.tag,
            "category": node.category,
            "note": _note(node.attrs),
            "path": self.path(node.id),
            "attrs": attrs,
            "links": [
                {
                    "id": target,
                    "direction": direction,
                    "name": self.nodes[target].name,
                    "label": self.label(target),
                    "kind": self.nodes[target].value_kind,
                    "category": self.nodes[target].category,
                    "hidden": self.nodes[target].hidden,
                }
                for target, direction in node.links
                if target in self.nodes
            ],
        }
        if node.is_resource:
            result["kind"] = node.value_kind
            typedef = node.attrs.get("typedef")
            if node.value_kind == "enum" and typedef:
                try:
                    enum = self.enums.get(parse_id(typedef))
                except ValueError:
                    enum = None
                if enum:
                    result["enum"] = enum
                    initial = node.attrs.get("inivalue")
                    if initial:
                        try:
                            value = self.enum_values.get(parse_id(initial))
                        except ValueError:
                            value = None
                        if value:
                            result["attrs"]["inivalue"] = value["name"]
        return result

    def resources(self) -> list[dict[str, Any]]:
        """Every shown resource with its place, link count and whether it sits in a product or a function block."""
        result = []
        for node in self.nodes.values():
            if not node.is_resource or node.hidden:
                continue
            owner = self.nodes.get(node.parent)
            while owner is not None and owner.id != ROOT_ID and owner.category not in ("product", "functionblock"):
                owner = self.nodes.get(owner.parent)
            result.append({
                "id": node.id, "name": node.name, "tag": node.tag, "kind": node.value_kind, "label": self.label(node.id),
                "links": len(node.links), "owner": owner.category if owner is not None and owner.id != ROOT_ID else None,
                "section": self.nodes[node.parent].tag if node.parent in self.nodes else None,
            })
        return result

    def kinds(self, ids: list[int]) -> dict[int, str]:
        """Value kind per known resource id (used to interpret live values)."""
        return {i: self.nodes[i].value_kind for i in ids if i in self.nodes and self.nodes[i].is_resource}

    def search(self, query: str, view: str = VIEW_ALL, limit: int = 200) -> list[dict[str, Any]]:
        """Find nodes by name, or by resource id (decimal or ``0x`` hex)."""
        query = query.strip().lower()
        if not query:
            return []
        wanted_id: int | None = None
        try:
            wanted_id = int(query, 16) if query.startswith("0x") else int(query)
        except ValueError:
            pass
        found: list[dict[str, Any]] = []
        for node in self.nodes.values():
            if node.id == ROOT_ID or node.category == "section":
                continue
            if node.id == wanted_id or query in node.name.lower() or (
                wanted_id is not None and str(node.id).startswith(query)
            ):
                if not self._path_visible(node, view):
                    continue
                entry = self.summary(node, view)
                entry["label"] = self.label(node.id)
                found.append(entry)
                if len(found) >= limit:
                    break
        return found

    def _path_visible(self, node: Node, view: str) -> bool:
        current: Node | None = node
        while current is not None and current.id != ROOT_ID:
            if not self._visible(current, view):
                return False
            current = self.nodes.get(current.parent)
        return True
