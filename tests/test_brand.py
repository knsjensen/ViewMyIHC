"""The logo shown in Home Assistant's "Add integration" dialog lives in ``custom_components/viewmyihc/brand/``."""

from __future__ import annotations

from pathlib import Path
import struct

import pytest

BRAND = Path(__file__).resolve().parents[1] / "custom_components" / "viewmyihc" / "brand"
PNG = b"\x89PNG\r\n\x1a\n"

# file -> (width, height); square icons, landscape logos (shorter side 128 px, 256 px for @2x)
EXPECTED = {
    "icon.png": (256, 256),
    "icon@2x.png": (512, 512),
    "logo.png": None,
    "logo@2x.png": None,
    "dark_logo.png": None,
    "dark_logo@2x.png": None,
}


def size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == PNG, f"{path.name} is not a PNG"
    return struct.unpack(">II", data[16:24])


@pytest.mark.parametrize("name", EXPECTED)
def test_brand_image_is_a_valid_png_of_the_right_shape(name):
    width, height = size(BRAND / name)
    if EXPECTED[name]:
        assert (width, height) == EXPECTED[name]
    else:  # landscape logo
        assert width > height
        assert height == (256 if "@2x" in name else 128)


def test_only_filenames_home_assistant_serves_are_used():
    pytest.importorskip("homeassistant.components.brands.const")
    from homeassistant.components.brands.const import ALLOWED_IMAGES

    assert {p.name for p in BRAND.glob("*.png")} <= set(ALLOWED_IMAGES)


def test_home_assistant_detects_the_branding_folder():
    pytest.importorskip("homeassistant.loader")
    from homeassistant.loader import Integration

    # has_branding is simply "brand" in the integration's top-level files
    assert (BRAND.parent / "brand").is_dir()
    assert hasattr(Integration, "has_branding")


def test_svg_source_is_kept_for_future_edits():
    assert (BRAND.parents[2] / "assets" / "brand" / "icon.svg").read_text(encoding="utf-8").startswith("<svg")
