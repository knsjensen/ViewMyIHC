"""Find where the user's ``ihc:`` setup lives and where a new entry belongs in it. Read only.

Nothing here writes or changes any file. The module follows ``!include`` references the way Home Assistant does
(relative to the file that contains the tag), also through ``homeassistant: packages:``, and reports

* in which file and on which line the ``ihc:`` controller is defined,
* for each platform list (binary_sensor, light, sensor, switch) where it is and which entries it already holds,
* for a new entry: exactly where to paste it (file, after which line, with which indentation).

YAML is *composed* (not constructed) with PyYAML, which gives exact line numbers and leaves ``!secret`` and other
tags unresolved: secrets are never read. Only files inside the configuration directory are opened.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

from .entity_config import PLATFORMS, render_entry

INCLUDE = "!include"
DIR_LIST = "!include_dir_list"
DIR_MERGE_LIST = "!include_dir_merge_list"
DIR_NAMED = "!include_dir_named"
DIR_MERGE_NAMED = "!include_dir_merge_named"

MAX_FILES = 300
MAX_BYTES = 2_000_000
MAX_DEPTH = 16


def _normalise_url(url: str) -> str:
    url = url.strip().lower()
    for prefix in ("https://", "http://"):
        if url.startswith(prefix):
            url = url[len(prefix):]
    return url.rstrip("/")


def _items(node: Node | None) -> list[tuple[str, ScalarNode, Node]]:
    """``(key text, key node, value node)`` for the plain keys of a mapping."""
    if not isinstance(node, MappingNode):
        return []
    return [(key.value, key, value) for key, value in node.value if isinstance(key, ScalarNode)]


def _get(node: Node | None, name: str) -> tuple[ScalarNode, Node] | None:
    for key_text, key, value in _items(node):
        if key_text == name:
            return key, value
    return None


def _plain_scalar(node: Node | None) -> str | None:
    """The text of an ordinary scalar (not ``!secret``, ``!include`` and the like)."""
    if isinstance(node, ScalarNode) and not node.tag.startswith("!"):
        return str(node.value)
    return None


def _last_line(node: Node) -> int:
    """1-based number of the last line a node occupies."""
    end = node.end_mark
    return end.line + (0 if end.column == 0 else 1)


class _Scanner:
    """Loads and follows the configuration files."""

    def __init__(self, config_dir: Path) -> None:
        self.root = config_dir.resolve()
        self._cache: dict[Path, Node | None] = {}
        self.scanned: list[str] = []
        self.problems: list[dict[str, Any]] = []

    def rel(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def _inside(self, path: Path) -> bool:
        resolved = path.resolve()
        return resolved == self.root or self.root in resolved.parents

    def problem(self, level: str, code: str, *, file: str | None = None, line: int | None = None, **params: Any) -> None:
        entry = {"level": level, "code": code, "params": params, "file": file, "line": line}
        if entry not in self.problems:
            self.problems.append(entry)

    def target(self, node: ScalarNode, base: Path) -> Path:
        """Include paths are relative to the directory of the file that contains the tag (as in Home Assistant)."""
        return Path(os.path.normpath(base.parent / str(node.value)))

    def load(self, path: Path, via: ScalarNode | None = None, via_file: Path | None = None) -> Node | None:
        path = Path(os.path.normpath(path))
        where = {"file": self.rel(via_file), "line": via.start_mark.line + 1} if via is not None and via_file else {}
        if not self._inside(path):
            self.problem("info", "outside_config", path=str(path), **where)
            return None
        key = path.resolve()
        if key in self._cache:
            return self._cache[key]
        self._cache[key] = None
        if not path.is_file():
            self.problem("warn", "include_missing", path=self.rel(path), **where)
            return None
        if len(self.scanned) >= MAX_FILES:
            self.problem("warn", "too_many_files", limit=MAX_FILES)
            return None
        try:
            if path.stat().st_size > MAX_BYTES:
                self.problem("info", "file_too_large", path=self.rel(path))
                return None
            node = yaml.compose(path.read_text(encoding="utf-8"), Loader=yaml.SafeLoader)
        except (OSError, UnicodeDecodeError) as err:
            self.problem("warn", "unreadable", path=self.rel(path), error=str(err))
            return None
        except yaml.YAMLError as err:
            mark = getattr(err, "problem_mark", None)
            self.problem("warn", "parse_error", file=self.rel(path), line=(mark.line + 1) if mark else None,
                         error=str(getattr(err, "problem", None) or err))
            return None
        self.scanned.append(self.rel(path))
        self._cache[key] = node
        return node

    def dir_files(self, directory: Path, via: ScalarNode, via_file: Path) -> list[Path]:
        """YAML files in a directory, like Home Assistant's ``_find_files`` (recursive, skips hidden)."""
        directory = Path(os.path.normpath(directory))
        where = {"file": self.rel(via_file), "line": via.start_mark.line + 1}
        if not self._inside(directory):
            self.problem("info", "outside_config", path=str(directory), **where)
            return []
        if not directory.is_dir():
            self.problem("warn", "include_missing", path=self.rel(directory), **where)
            return []
        found: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(directory, followlinks=True):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for name in sorted(filenames):
                if name.endswith(".yaml") and not name.startswith("."):
                    found.append(Path(dirpath) / name)
        return found

    def expand(self, node: Node | None, base: Path, depth: int = 0) -> list[tuple[MappingNode, Path]]:
        """The mapping elements of a list-like value, following includes. ``(mapping node, file)``."""
        if node is None or depth > MAX_DEPTH:
            return []
        if node.tag == INCLUDE and isinstance(node, ScalarNode):
            target = self.target(node, base)
            return self.expand(self.load(target, node, base), target, depth + 1)
        if node.tag in (DIR_LIST, DIR_MERGE_LIST) and isinstance(node, ScalarNode):
            out: list[tuple[MappingNode, Path]] = []
            for file in self.dir_files(self.target(node, base), node, base):
                out.extend(self.expand(self.load(file, node, base), file, depth + 1))
            return out
        if isinstance(node, SequenceNode):
            out = []
            for item in node.value:
                out.extend(self.expand(item, base, depth + 1))
            return out
        if isinstance(node, MappingNode):
            return [(node, base)]
        return []

    def follow_mapping(self, node: Node | None, base: Path, depth: int = 0) -> tuple[MappingNode, Path] | None:
        if node is None or depth > MAX_DEPTH:
            return None
        if node.tag == INCLUDE and isinstance(node, ScalarNode):
            target = self.target(node, base)
            return self.follow_mapping(self.load(target, node, base), target, depth + 1)
        if isinstance(node, MappingNode):
            return node, base
        return None

    def packages(self, node: Node | None, base: Path, depth: int = 0) -> list[tuple[MappingNode, Path]]:
        """Every package mapping below ``homeassistant: packages:``."""
        if node is None or depth > MAX_DEPTH:
            return []
        out: list[tuple[MappingNode, Path]] = []
        if node.tag == INCLUDE and isinstance(node, ScalarNode):
            target = self.target(node, base)
            return self.packages(self.load(target, node, base), target, depth + 1)
        if node.tag in (DIR_NAMED, DIR_MERGE_NAMED) and isinstance(node, ScalarNode):
            for file in self.dir_files(self.target(node, base), node, base):
                root = self.load(file, node, base)
                if node.tag == DIR_NAMED:
                    if isinstance(root, MappingNode):
                        out.append((root, file))
                else:
                    out.extend(self.packages(root, file, depth + 1))
            return out
        if isinstance(node, MappingNode):
            for _name, _key, value in _items(node):
                followed = self.follow_mapping(value, base, depth + 1)
                if followed:
                    out.append(followed)
        return out

    def find_controllers(self, config_file: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        root = self.load(config_file)
        if not isinstance(root, MappingNode):
            return [], None
        candidates: list[tuple[MappingNode, Path]] = [(root, config_file)]
        core = _get(root, "homeassistant")
        if core:
            followed = self.follow_mapping(core[1], config_file)
            if followed:
                packages = _get(followed[0], "packages")
                if packages:
                    candidates.extend(self.packages(packages[1], followed[1]))
        controllers: list[dict[str, Any]] = []
        ihc_key: dict[str, Any] | None = None
        for mapping, file in candidates:
            found = _get(mapping, "ihc")
            if not found:
                continue
            key, value = found
            ihc_key = ihc_key or {"file": self.rel(file), "line": key.start_mark.line + 1}
            for controller, controller_file in self.expand(value, file):
                controllers.append({"node": controller, "file": controller_file})
        return controllers, ihc_key


def _entries(scanner: _Scanner, value: Node | None, base: Path) -> list[dict[str, Any]]:
    """The entries below a platform key, with where they sit (file, first and last line, dash column)."""
    result = []
    for entry, entry_file in scanner.expand(value, base):
        id_node = _get(entry, "id")
        text = _plain_scalar(id_node[1]) if id_node else None
        if text is None or not text.strip().isdigit():
            continue
        name = _get(entry, "name")
        result.append(
            {
                "id": int(text),
                "name": _plain_scalar(name[1]) if name else None,
                "file": scanner.rel(entry_file),
                "line": id_node[0].start_mark.line + 1,
                "end_line": _last_line(entry),
                "indent": max(entry.start_mark.column - 2, 0),  # the "- " sits two columns before the first key
            }
        )
    return result


def _describe_platform(scanner: _Scanner, controller: MappingNode, base: Path, platform: str) -> dict[str, Any]:
    """The platform key of a controller: ``missing``, ``inline``, ``include``, ``dir`` or ``other`` (e.g. !secret)."""
    found = _get(controller, platform)
    if not found:
        return {"state": "missing", "entries": [], "container": None}
    key, value = found
    info: dict[str, Any] = {"state": "other", "file": scanner.rel(base), "line": key.start_mark.line + 1, "entries": []}
    container: dict[str, Any] | None = None
    if isinstance(value, ScalarNode) and value.tag == INCLUDE:
        target = scanner.target(value, base)
        info["state"], info["include"] = "include", scanner.rel(target)
        root = scanner.load(target, value, base)
        entries = _entries(scanner, value, base)
        in_file = [e for e in entries if e["file"] == scanner.rel(target)]
        container = {
            "file": scanner.rel(target),
            "after_line": max((e["end_line"] for e in in_file), default=0),
            "indent": in_file[0]["indent"] if in_file else 0,
            # a block list can be appended to; so can an existing but empty file (a top-level list starts there)
            "usable": (isinstance(root, SequenceNode) and not root.flow_style) or (root is None and target.is_file()),
        }
        info["entries"] = entries
    elif isinstance(value, ScalarNode) and value.tag in (DIR_LIST, DIR_MERGE_LIST):
        directory = scanner.target(value, base)
        info["state"], info["include"] = "dir", scanner.rel(directory)
        info["entries"] = _entries(scanner, value, base)
        container = {"dir": scanner.rel(directory)}
    elif isinstance(value, SequenceNode):
        info["state"] = "inline"
        info["entries"] = _entries(scanner, value, base)
        container = {
            "file": scanner.rel(base),
            "after_line": max((e["end_line"] for e in info["entries"]), default=_last_line(key)),
            "indent": info["entries"][0]["indent"] if info["entries"] else key.start_mark.column + 2,
            "usable": not value.flow_style,
        }
    info["container"] = container
    return info


def check_setup(config_dir: str | Path, controller_url: str | None) -> dict[str, Any]:
    """Locate the ihc setup (read only). ``controller_url`` is the url Home Assistant is connected to."""
    config_dir = Path(config_dir)
    scanner = _Scanner(config_dir)
    config_file = config_dir / "configuration.yaml"
    result: dict[str, Any] = {
        "config_dir_ok": config_file.is_file(),
        "ihc_defined_in": None,
        "controllers": [],
        "chosen": None,
        "platforms": {},
        "problems": scanner.problems,
        "scanned": scanner.scanned,
        "status": "unknown",
    }
    if not config_file.is_file():
        scanner.problem("warn", "no_configuration")
        return result

    controllers, ihc_key = scanner.find_controllers(config_file)
    result["ihc_defined_in"] = ihc_key
    if not controllers:
        scanner.problem("warn", "no_ihc" if ihc_key is None else "ihc_empty")
        result["status"] = "no_ihc"
        return result

    wanted = _normalise_url(controller_url) if controller_url else None
    described: list[dict[str, Any]] = []
    for item in controllers:
        node: MappingNode = item["node"]
        file: Path = item["file"]
        url_pair = _get(node, "url")
        url = _plain_scalar(url_pair[1]) if url_pair else None
        auto = _get(node, "auto_setup")
        auto_text = (_plain_scalar(auto[1]) or "").lower() if auto else ""
        # new keys go below a key with a simple one-line value, so an indented block is never split
        simple = [k for _t, k, v in _items(node) if isinstance(v, ScalarNode)]
        anchor = url_pair[0] if url_pair and isinstance(url_pair[1], ScalarNode) else (simple[0] if simple else None)
        described.append(
            {
                "file": scanner.rel(file),
                "line": node.start_mark.line + 1,
                "url": url,
                "url_known": url is not None,
                "matches": (_normalise_url(url) == wanted) if (url and wanted) else None,
                "auto_setup": auto_text not in ("false", "no", "off"),
                "anchor": {"line": anchor.start_mark.line + 1, "column": anchor.start_mark.column} if anchor else None,
                "_node": node,
                "_base": file,
            }
        )

    public = [{k: v for k, v in c.items() if not k.startswith("_")} for c in described]
    result["controllers"] = public
    matching = [c for c in described if c["matches"] is True]
    chosen = matching[0] if len(matching) == 1 else (described[0] if len(described) == 1 else None)
    if chosen is None:
        scanner.problem("warn", "ambiguous_controller", count=len(described))
        result["status"] = "ambiguous"
        return result
    result["chosen"] = {k: v for k, v in chosen.items() if not k.startswith("_")}
    if chosen["url"] is None:
        scanner.problem("info", "url_not_literal", file=chosen["file"], line=chosen["line"])
    elif chosen["matches"] is False:
        scanner.problem("warn", "url_differs", file=chosen["file"], line=chosen["line"], url=chosen["url"], controller=controller_url)
    for platform in PLATFORMS:
        result["platforms"][platform] = _describe_platform(scanner, chosen["_node"], chosen["_base"], platform)
    if chosen["auto_setup"]:
        scanner.problem("info", "auto_setup_on", file=chosen["file"], line=chosen["line"])
    result["status"] = "ok"
    return result


def placement(setup: dict[str, Any], platform: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Where and how to paste ``entry`` into the user's setup, with the text already indented correctly.

    ``mode``: ``append`` (into an existing list, below ``after_line`` of ``file``), ``add_key`` (a new ``platform:`` key
    below ``after_line`` of the controller's file), ``new_file`` (a new file in the included directory ``dir``) or
    ``manual`` (the structure cannot be followed; the generic text is given).
    """
    chosen = setup.get("chosen")
    info = (setup.get("platforms") or {}).get(platform)
    generic = f"{platform}:\n{render_entry(entry, 2)}"
    if chosen is None or info is None:
        return {"mode": "manual", "text": generic, "reason": setup.get("status", "unknown")}
    container = info.get("container")
    state = info["state"]
    if state in ("inline", "include") and container and container.get("usable"):
        return {
            "mode": "append",
            "file": container["file"],
            "after_line": container["after_line"],
            "text": render_entry(entry, container["indent"]),
            "key": {"file": info["file"], "line": info["line"]},
        }
    if state == "dir" and container:
        return {"mode": "new_file", "dir": container["dir"], "text": render_entry(entry, 0), "key": {"file": info["file"], "line": info["line"]}}
    if state == "missing" and chosen.get("anchor"):
        column = chosen["anchor"]["column"]
        return {
            "mode": "add_key",
            "file": chosen["file"],
            "after_line": chosen["anchor"]["line"],
            "text": f"{' ' * column}{platform}:\n{render_entry(entry, column + 2)}",
        }
    return {"mode": "manual", "text": generic, "reason": "unsupported_structure", "key": {"file": info.get("file"), "line": info.get("line")}}
