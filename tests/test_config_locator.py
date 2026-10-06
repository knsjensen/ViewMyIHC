"""The locator must cope with the many ways people split their configuration, and must never write anything."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from conftest import load_module

URL = "http://192.168.1.3"


@pytest.fixture(scope="module")
def loc():
    return load_module("config_locator")


@pytest.fixture(scope="module")
def ec():
    return load_module("entity_config")


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def snapshot(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha1(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def run(loc, root, url=URL):
    before = snapshot(root)
    result = loc.check_setup(root, url)
    assert snapshot(root) == before, "the check must not change any file"
    return result


def codes(result):
    return {p["code"] for p in result["problems"]}


def new_entry(ec, platform="switch", id=514, name="Lampe", **options):
    return ec.validate_entry({"platform": platform, "id": id, "name": name, "options": options})


# ------------------------------------------------------------------ where is ihc:


def test_ihc_inline_in_configuration_yaml(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "default_config:\n\nihc:\n  - url: http://192.168.1.3\n    username: u\n    password: p\n")
    r = run(loc, tmp_path)
    assert r["ihc_defined_in"] == {"file": "configuration.yaml", "line": 3}
    assert (r["chosen"]["file"], r["chosen"]["line"], r["chosen"]["matches"], r["status"]) == ("configuration.yaml", 4, True, "ok")


def test_ihc_in_its_own_file_referenced_from_configuration(loc, tmp_path):
    """The user's own case: `ihc: !include ihc.yaml`."""
    write(tmp_path, "configuration.yaml", "default_config:\nihc: !include ihc.yaml\n")
    write(tmp_path, "ihc.yaml", "- url: http://192.168.1.3\n  username: u\n  password: p\n  auto_setup: false\n")
    r = run(loc, tmp_path)
    assert r["ihc_defined_in"] == {"file": "configuration.yaml", "line": 2}
    assert (r["chosen"]["file"], r["chosen"]["line"], r["chosen"]["auto_setup"]) == ("ihc.yaml", 1, False)
    assert "auto_setup_on" not in codes(r)


def test_reference_of_a_reference_and_secrets(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "homeassistant:\n  customize: !include customize.yaml\nihc: !include integrations/ihc.yaml\n")
    write(tmp_path, "integrations/ihc.yaml", "- url: !secret ihc_url\n  username: u\n  password: !secret ihc_pw\n  switch: !include ../ihc/switch.yaml\n")
    write(tmp_path, "ihc/switch.yaml", "- id: 100\n  name: Egen\n")
    write(tmp_path, "customize.yaml", "{}\n")
    r = run(loc, tmp_path)
    assert (r["chosen"]["file"], r["chosen"]["url"], r["chosen"]["url_known"]) == ("integrations/ihc.yaml", None, False)
    assert r["platforms"]["switch"]["state"] == "include" and [e["id"] for e in r["platforms"]["switch"]["entries"]] == [100]
    assert "url_not_literal" in codes(r)


def test_ihc_inside_a_package_file_and_a_package_directory(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "homeassistant:\n  packages: !include_dir_named packages\n")
    write(tmp_path, "packages/lights.yaml", "light:\n  - platform: group\n")
    write(tmp_path, "packages/ihc.yaml", "ihc:\n  - url: http://192.168.1.3\n    username: u\n    password: p\n")
    r = run(loc, tmp_path)
    assert r["ihc_defined_in"] == {"file": "packages/ihc.yaml", "line": 1} and r["chosen"]["file"] == "packages/ihc.yaml"


def test_ihc_in_inline_packages_mapping_and_merge_named(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "homeassistant:\n  packages:\n    a: !include pkg_a.yaml\n    b:\n      ihc:\n        url: http://192.168.1.3\n")
    write(tmp_path, "pkg_a.yaml", "sensor: []\n")
    assert (run(loc, tmp_path)["chosen"]["file"], run(loc, tmp_path)["chosen"]["line"]) == ("configuration.yaml", 6)
    write(tmp_path, "configuration.yaml", "homeassistant:\n  packages: !include_dir_merge_named pk\n")
    write(tmp_path, "pk/one.yaml", "mine:\n  ihc:\n    - url: http://192.168.1.3\n")
    assert run(loc, tmp_path)["chosen"]["file"] == "pk/one.yaml"


def test_ihc_list_split_over_a_directory_picks_the_connected_controller_by_url(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc: !include_dir_merge_list ihc_controllers\n")
    write(tmp_path, "ihc_controllers/a.yaml", "- url: http://192.168.1.99\n- url: http://192.168.1.3\n")
    r = run(loc, tmp_path)
    assert len(r["controllers"]) == 2 and (r["chosen"]["url"], r["chosen"]["matches"]) == ("http://192.168.1.3", True)


def test_no_ihc_no_configuration_and_ambiguous(loc, tmp_path):
    assert run(loc, tmp_path)["config_dir_ok"] is False
    write(tmp_path, "configuration.yaml", "default_config:\n")
    assert run(loc, tmp_path)["status"] == "no_ihc" and "no_ihc" in codes(run(loc, tmp_path))
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: !secret a\n  - url: !secret b\n")
    r = run(loc, tmp_path)
    assert r["status"] == "ambiguous" and r["chosen"] is None and len(r["controllers"]) == 2


def test_url_that_differs_and_auto_setup_default(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://10.0.0.5\n")
    r = run(loc, tmp_path, url="http://192.168.1.3/")
    assert "url_differs" in codes(r) and "auto_setup_on" in codes(r) and r["chosen"]["matches"] is False


# ------------------------------------------------------------------ the platform lists


def test_each_platform_is_described_with_its_entries_and_lines(loc, tmp_path):
    write(
        tmp_path,
        "configuration.yaml",
        "ihc:\n  - url: http://192.168.1.3\n    switch:\n      - id: 100\n        name: A\n      - id: 101\n    light: !include l.yaml\n    sensor: !include_dir_merge_list s\n",
    )
    write(tmp_path, "l.yaml", "- id: 200\n  name: L\n")
    write(tmp_path, "s/x.yaml", "- id: 300\n")
    p = run(loc, tmp_path)["platforms"]
    assert [(p["switch"]["state"], e["id"], e["line"], e["file"]) for e in p["switch"]["entries"]] == [
        ("inline", 100, 4, "configuration.yaml"), ("inline", 101, 6, "configuration.yaml")]
    assert (p["light"]["state"], p["light"]["include"], p["light"]["entries"][0]["file"]) == ("include", "l.yaml", "l.yaml")
    assert (p["sensor"]["state"], p["sensor"]["include"]) == ("dir", "s")
    assert p["binary_sensor"]["state"] == "missing"


# ------------------------------------------------------------------ where a new entry goes (placement)


def place(loc, ec, root, platform="switch", **kw):
    setup = run(loc, root)
    return loc.placement(setup, platform, new_entry(ec, platform, **kw))


def apply(root: Path, p: dict, loc_dir: Path | None = None) -> None:
    """Do what the user does: insert p["text"] below p["after_line"] of p["file"]."""
    path = root / p["file"]
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    lines[p["after_line"]:p["after_line"]] = p["text"].splitlines()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_append_below_the_last_entry_of_an_inline_list_with_matching_indentation(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch:\n      - id: 100\n        name: A\n")
    p = place(loc, ec, tmp_path)
    assert (p["mode"], p["file"], p["after_line"]) == ("append", "configuration.yaml", 5)
    assert p["text"].splitlines()[0] == '      - id: 514'
    apply(tmp_path, p)
    data = yaml.safe_load((tmp_path / "configuration.yaml").read_text(encoding="utf-8"))
    assert [e["id"] for e in data["ihc"][0]["switch"]] == [100, 514]


def test_append_into_the_users_own_included_file(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc: !include ihc.yaml\n")
    write(tmp_path, "ihc.yaml", "- url: http://192.168.1.3\n  switch: !include switches.yaml\n")
    write(tmp_path, "switches.yaml", "- id: 100\n  name: A\n  on_id: 5\n")
    p = place(loc, ec, tmp_path)
    assert (p["mode"], p["file"], p["after_line"], p["key"]) == ("append", "switches.yaml", 3, {"file": "ihc.yaml", "line": 2})
    apply(tmp_path, p)
    assert [e["id"] for e in yaml.safe_load((tmp_path / "switches.yaml").read_text(encoding="utf-8"))] == [100, 514]


def test_append_to_an_existing_but_empty_included_file(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch: !include s.yaml\n")
    write(tmp_path, "s.yaml", "")
    p = place(loc, ec, tmp_path)
    assert (p["mode"], p["file"], p["after_line"]) == ("append", "s.yaml", 0)
    apply(tmp_path, p)
    assert yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8")) == [{"id": 514, "name": "Lampe"}]


def test_missing_platform_key_is_added_below_a_simple_key_of_the_controller(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "default_config:\nihc: !include ihc.yaml\n")
    write(tmp_path, "ihc.yaml", "- url: http://192.168.1.3\n  username: u\n  password: p\n")
    p = place(loc, ec, tmp_path, "sensor", id=20, name="Temp", unit_of_measurement="°C")
    assert (p["mode"], p["file"], p["after_line"]) == ("add_key", "ihc.yaml", 1)
    apply(tmp_path, p)
    data = yaml.safe_load((tmp_path / "ihc.yaml").read_text(encoding="utf-8"))
    assert data[0]["sensor"] == [{"id": 20, "name": "Temp", "unit_of_measurement": "°C"}] and data[0]["url"] == "http://192.168.1.3"


def test_the_new_key_never_splits_an_indented_block(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - info:\n      nested: 1\n    url: http://192.168.1.3\n    username: u\n")
    p = place(loc, ec, tmp_path)
    assert p["mode"] == "add_key" and p["after_line"] == 4  # below `url:`, not below `info:`
    apply(tmp_path, p)
    assert yaml.safe_load((tmp_path / "configuration.yaml").read_text(encoding="utf-8"))["ihc"][0]["switch"][0]["id"] == 514


def test_directory_include_gets_a_new_file_suggestion(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch: !include_dir_merge_list sw\n")
    write(tmp_path, "sw/a.yaml", "- id: 100\n")
    p = place(loc, ec, tmp_path)
    assert (p["mode"], p["dir"], p["text"]) == ("new_file", "sw", '- id: 514\n  name: "Lampe"')


def test_flow_style_secret_or_unknown_structure_falls_back_to_the_generic_text(loc, ec, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch: [{id: 100}]\n")
    p = place(loc, ec, tmp_path)
    assert p["mode"] == "manual" and p["text"].startswith("switch:\n  - id: 514")
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch: !secret sw\n")
    assert place(loc, ec, tmp_path)["mode"] == "manual"
    write(tmp_path, "configuration.yaml", "default_config:\n")
    assert place(loc, ec, tmp_path)["mode"] == "manual"


def test_the_placed_entry_is_found_by_the_next_check(loc, ec, tmp_path):
    """Paste, check again: the entry is now reported (so the dialog can confirm that it was inserted)."""
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch:\n      - id: 100\n")
    apply(tmp_path, place(loc, ec, tmp_path))
    ids = [e["id"] for e in run(loc, tmp_path)["platforms"]["switch"]["entries"]]
    assert ids == [100, 514]


# ------------------------------------------------------------------ robustness


def test_broken_yaml_and_missing_includes_are_reported_not_raised(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc: !include ihc.yaml\nother: !include nowhere.yaml\n")
    write(tmp_path, "ihc.yaml", "- url: [unclosed\n")
    r = run(loc, tmp_path)
    parse = next(p for p in r["problems"] if p["code"] == "parse_error")
    assert r["status"] == "no_ihc" and parse["file"] == "ihc.yaml" and parse["line"] >= 1


def test_missing_include_target_names_the_line_that_refers_to_it(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: http://192.168.1.3\n    switch: !include gone.yaml\n")
    missing = next(p for p in run(loc, tmp_path)["problems"] if p["code"] == "include_missing")
    assert (missing["file"], missing["line"], missing["params"]["path"]) == ("configuration.yaml", 3, "gone.yaml")


def test_include_cycles_do_not_hang(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc: !include a.yaml\n")
    write(tmp_path, "a.yaml", "!include b.yaml\n")
    write(tmp_path, "b.yaml", "!include a.yaml\n")
    assert run(loc, tmp_path)["status"] == "no_ihc"


def test_files_outside_the_config_directory_are_never_opened(loc, tmp_path):
    write(tmp_path / "outside", "ihc.yaml", "- url: http://192.168.1.3\n")
    write(tmp_path / "config", "configuration.yaml", "ihc: !include ../outside/ihc.yaml\n")
    r = run(loc, tmp_path / "config")
    assert "outside_config" in codes(r) and r["status"] == "no_ihc" and "outside/ihc.yaml" not in " ".join(r["scanned"])


def test_secrets_file_is_never_read(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc:\n  - url: !secret ihc_url\n    password: !secret ihc_pw\n")
    write(tmp_path, "secrets.yaml", "ihc_url: http://192.168.1.3\nihc_pw: hemmelig\n")
    r = run(loc, tmp_path)
    assert "secrets.yaml" not in r["scanned"] and "hemmelig" not in repr(r)


def test_hidden_directories_and_files_are_skipped_like_home_assistant(loc, tmp_path):
    write(tmp_path, "configuration.yaml", "ihc: !include_dir_merge_list ctl\n")
    write(tmp_path, "ctl/ok.yaml", "- url: http://192.168.1.3\n")
    write(tmp_path, "ctl/.hidden/x.yaml", "- url: http://10.9.9.9\n")
    write(tmp_path, "ctl/.old.yaml", "- url: http://10.8.8.8\n")
    assert len(run(loc, tmp_path)["controllers"]) == 1
