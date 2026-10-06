"""Keep a copy of every project revision that ViewMyIHC downloads from the controller.

Plain file I/O (no Home Assistant imports, blocking: run in the executor). Each controller gets a folder with
gzip-compressed project files (``.vis`` content as the controller sends it, ISO-8859-1) and an ``index.json``.
A download identical to the newest copy is not stored again. The files hold everything the project holds, including
customer data and the SMS modem's PIN code, so they stay in Home Assistant's private ``.storage`` folder.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

KEEP = 30
# "ihc": the IHC Visual project (gzip-compressed .vis); "scene": the SceneDesign project, kept as the .icz file it is
_NAME = {"ihc": re.compile(r"^\d{8}-\d{6}-[0-9a-f]{8}\.vis\.gz$"), "scene": re.compile(r"^\d{8}-\d{6}-[0-9a-f]{8}\.icz$")}
_SUFFIX = {"ihc": ".vis.gz", "scene": ".icz"}
ENCODING = "iso-8859-1"


class BackupError(Exception):
    """Unknown or unreadable backup."""


def _folder(root: Path, serial: str, kind: str = "ihc") -> Path:
    base = root / re.sub(r"[^\w-]", "_", serial)
    return base if kind == "ihc" else base / kind


def _read_index(folder: Path) -> list[dict[str, Any]]:
    try:
        return json.loads((folder / "index.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return []


def list_backups(root: Path, serial: str, kind: str = "ihc") -> list[dict[str, Any]]:
    """Newest first."""
    return sorted(_read_index(_folder(root, serial, kind)), key=lambda e: e["saved"], reverse=True)


def save(root: Path, serial: str, xml: str, info: dict[str, Any], now: float | None = None) -> dict[str, Any] | None:
    """Store an IHC project unless it equals the newest copy. Returns the new index entry (or None)."""
    raw = xml.encode(ENCODING, errors="replace")
    return _store(root, serial, "ihc", raw, gzip.compress(raw), info, now)


def save_scene(root: Path, serial: str, icz: bytes, info: dict[str, Any], now: float | None = None) -> dict[str, Any] | None:
    """Store a SceneDesign project (.icz) unless it equals the newest copy."""
    return _store(root, serial, "scene", icz, icz, info, now)


def _store(root: Path, serial: str, kind: str, raw: bytes, stored: bytes, info: dict[str, Any], now: float | None) -> dict[str, Any] | None:
    digest = hashlib.sha256(raw).hexdigest()
    folder = _folder(root, serial, kind)
    entries = list_backups(root, serial, kind)
    if entries and entries[0]["sha256"] == digest:
        return None
    now = time.time() if now is None else now
    name = time.strftime("%Y%m%d-%H%M%S", time.localtime(now)) + f"-{digest[:8]}{_SUFFIX[kind]}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_bytes(stored)
    entry = {"name": name, "saved": now, "sha256": digest, "size": len(raw), **info}
    entries.insert(0, entry)
    for old in entries[KEEP:]:
        (folder / old["name"]).unlink(missing_ok=True)
    (folder / "index.json").write_text(json.dumps(entries[:KEEP], ensure_ascii=False, indent=1), encoding="utf-8")
    return entry


def read(root: Path, serial: str, name: str) -> str:
    """The project XML of one IHC project backup."""
    if not _NAME["ihc"].match(name) or name not in {e["name"] for e in list_backups(root, serial)}:
        raise BackupError(f"Unknown backup {name}")
    try:
        return gzip.decompress((_folder(root, serial) / name).read_bytes()).decode(ENCODING)
    except (OSError, EOFError) as err:
        raise BackupError(f"Backup {name} cannot be read: {err}") from err


def read_gzip(root: Path, serial: str, name: str) -> bytes:
    """The stored (compressed) file, for download."""
    read(root, serial, name)  # validates the name and the content
    return (_folder(root, serial) / name).read_bytes()


def read_scene(root: Path, serial: str, name: str) -> bytes:
    """A stored SceneDesign project (.icz bytes)."""
    if not _NAME["scene"].match(name) or name not in {e["name"] for e in list_backups(root, serial, "scene")}:
        raise BackupError(f"Unknown backup {name}")
    try:
        return (_folder(root, serial, "scene") / name).read_bytes()
    except OSError as err:
        raise BackupError(f"Backup {name} cannot be read: {err}") from err
