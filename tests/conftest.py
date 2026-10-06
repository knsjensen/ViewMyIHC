"""Import the pure-Python modules without running the package ``__init__`` (needs Home Assistant)."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "viewmyihc"

# a stand-in package so that the modules' relative imports (``from .const import ...``) work
_pkg = types.ModuleType("vmi")
_pkg.__path__ = [str(COMPONENT)]
sys.modules.setdefault("vmi", _pkg)


def load_module(name: str):
    return importlib.import_module(f"vmi.{name}")


@pytest.fixture(scope="session")
def parser():
    return load_module("project_parser")


@pytest.fixture(scope="session")
def bridge():
    return load_module("ihc_bridge")


@pytest.fixture(scope="session")
def admin():
    return load_module("admin_reader")


@pytest.fixture(scope="session")
def sample(parser):
    data = (ROOT / "tests" / "fixtures" / "sample_project.vis").read_bytes()
    return parser.Project(data)

