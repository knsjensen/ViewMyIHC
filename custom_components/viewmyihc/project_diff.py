"""What changed between two revisions of a project: added, removed and changed nodes (pure Python).

Only what the panel shows is compared (no sections, no internal settings or programs). Nodes are matched by their
IHC id, which IHC Visual keeps stable, so a renamed or moved resource is one change, not a removal plus an addition.
"""

from __future__ import annotations

from typing import Any

from .project_parser import ROOT_ID, Project

LIMIT = 500


def _shown(project: Project) -> dict[int, Any]:
    return {i: n for i, n in project.nodes.items() if i != ROOT_ID and not n.hidden and n.category != "section"}


def _entry(project: Project, node_id: int) -> dict[str, Any]:
    node = project.nodes[node_id]
    return {"id": node_id, "name": node.name, "label": project.label(node_id), "category": node.category,
            "kind": node.value_kind}


def _links(project: Project, node_id: int) -> set[tuple[int, str]]:
    return {(target, direction) for target, direction in project.nodes[node_id].links if target in project.nodes}


def _link_text(project: Project, link: tuple[int, str]) -> str:
    return f"{link[1]}:{project.label(link[0])}"


def diff(old: Project, new: Project) -> dict[str, Any]:
    before, after = _shown(old), _shown(new)
    added = [_entry(new, i) for i in sorted(after.keys() - before.keys())]
    removed = [_entry(old, i) for i in sorted(before.keys() - after.keys())]
    changed: list[dict[str, Any]] = []
    for node_id in sorted(before.keys() & after.keys()):
        a, b = before[node_id], after[node_id]
        changes: list[dict[str, Any]] = []
        if a.name != b.name:
            changes.append({"field": "name", "old": a.name, "new": b.name})
        if a.parent != b.parent:  # by id: renaming a location is one change, not one per node inside it
            changes.append({"field": "location", "old": old.label(a.parent), "new": new.label(b.parent)})
        for key in sorted(set(a.attrs) | set(b.attrs)):
            if a.attrs.get(key) != b.attrs.get(key):
                changes.append({"field": key, "old": a.attrs.get(key), "new": b.attrs.get(key)})
        links_before, links_after = _links(old, node_id), _links(new, node_id)
        if links_before != links_after:
            changes.append({"field": "links",
                            "added": sorted(_link_text(new, link) for link in links_after - links_before),
                            "removed": sorted(_link_text(old, link) for link in links_before - links_after)})
        if changes:
            changed.append({**_entry(new, node_id), "changes": changes})
    return {
        "added": added[:LIMIT], "removed": removed[:LIMIT], "changed": changed[:LIMIT],
        "counts": {"added": len(added), "removed": len(removed), "changed": len(changed)},
    }
