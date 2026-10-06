"""manifest.json, const.VERSION and the panel's PANEL_VERSION must always be the same number."""

from __future__ import annotations

import json
from pathlib import Path
import re

from conftest import load_module

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "viewmyihc"


def test_manifest_const_and_panel_versions_match():
    manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))["version"]
    const = load_module("const").VERSION
    panel = re.search(r'const PANEL_VERSION = "([^"]+)"', (COMPONENT / "frontend" / "viewmyihc-panel.js").read_text(encoding="utf-8")).group(1)
    assert manifest == const == panel


def test_panel_compares_versions_and_warns_about_an_old_backend():
    js = (COMPONENT / "frontend" / "viewmyihc-panel.js").read_text(encoding="utf-8")
    assert "status.version" in js and "_renderVersionBanner" in js
