from __future__ import annotations

import os
from pathlib import Path

import pytest


def test_parse_id_hex_to_integer(parser):
    assert parser.parse_id("_0x16837") == 92215
    assert parser.parse_id("_0x0") == 0
    assert parser.parse_id("123") == 123


def test_invalid_xml_raises(parser):
    with pytest.raises(parser.ProjectError):
        parser.Project("<nope")
    with pytest.raises(parser.ProjectError):
        parser.Project("<other/>")


def test_project_info_hides_customer_data(sample):
    assert sample.info["version"] == "4.0"
    assert sample.info["modified"] == "2026-08-20 23:38"
    assert sample.info["description"] == "Testprojekt"
    assert "Test Person" not in repr(sample.info)


def test_root_groups_and_views(sample):
    all_groups = [c["name"] for c in sample.children(0)]
    assert all_groups == ["Køkken", "Kun programmer", "Kun installation"]
    inst = [c["name"] for c in sample.children(0, "installation")]
    assert inst == ["Køkken", "Kun installation"]
    prog = [c["name"] for c in sample.children(0, "programs")]
    assert prog == ["Køkken", "Kun programmer"]


def test_empty_locations_are_hidden_in_every_view(sample, parser):
    """A location without products, function blocks or programs (e.g. 'Carport') is noise in all views."""
    for view in ("all", "installation", "programs"):
        names = [c["name"] for c in sample.children(0, view)]
        assert "Tom lokalitet" not in names, view
        assert "Kun tomme undergrupper" not in names, view  # only contains an empty sub-group
    kitchen = parser.parse_id("_0x2132")
    for view in ("all", "installation", "programs"):
        assert all("Tom undergruppe" not in c["name"] for c in sample.children(kitchen, view)), view


def test_group_with_only_empty_children_reports_no_children(sample, parser):
    only_empty = sample.nodes[parser.parse_id("_0x2532")]
    assert sample.summary(only_empty, "all")["has_children"] is False


def test_empty_locations_are_not_found_by_search(sample):
    assert sample.search("Tom lokalitet") == []
    assert sample.search("tom undergruppe") == []


def test_view_filters_products_and_functionblocks(sample, parser):
    kitchen = parser.parse_id("_0x2132")
    assert {c["category"] for c in sample.children(kitchen, "installation")} == {"product"}
    assert {c["category"] for c in sample.children(kitchen, "programs")} == {"functionblock"}
    assert {c["category"] for c in sample.children(kitchen)} == {"product", "functionblock"}


def test_sections_and_resources(sample, parser):
    fb = parser.parse_id("_0x200")
    names = [c["name"] for c in sample.children(fb)]
    assert names == ["Input", "Output", "Indstillinger"]
    settings = sample.children(parser.parse_id("_0x206"))
    kinds = {c["name"]: c["kind"] for c in settings}
    assert kinds == {
        "Nat starter": "time",
        "Timer": "timer",
        "Ur valg": "enum",
        "Rumtemperatur": "temperature",
    }


def test_programs_and_their_resources_are_indexed_but_never_shown(sample, parser):
    program, inner = parser.parse_id("_0x20c"), parser.parse_id("_0x20d")
    # pass-through elements still put the program's resource directly under the program
    assert sample.nodes[inner].parent == program and sample.nodes[inner].hidden
    for view in ("all", "programs", "installation"):
        assert sample.children(program, view) == []
        assert sample.search("Tidspunkt", view) == []
    assert sample.info["resources"] == 9


def test_internal_settings_are_hidden_but_links_to_them_still_resolve(parser):
    project = parser.Project(
        '<utcs_project version_major="4" version_minor="0"><group id="_0x1" name="Rum">'
        '<functionblock id="_0x10" name="Blok">'
        '<inputs id="_0x11"><resource_input id="_0x12" name="Ind"><link_to_resource id="_0x13" link="_0x23"/></resource_input></inputs>'
        '<internalsettings id="_0x20"><resource_flag id="_0x22" name="Hjælpeflag"><link_from_resource id="_0x23" link="_0x13"/></resource_flag></internalsettings>'
        "</functionblock></group></utcs_project>"
    )
    assert [c["name"] for c in project.children(0x10)] == ["Input"]
    assert project.search("Hjælpeflag") == []
    link = project.detail(0x12)["links"][0]
    assert (link["name"], link["hidden"]) == ("Hjælpeflag", True)


def test_links_resolve_in_both_directions(sample, parser):
    pushbutton = parser.parse_id("_0x101")
    block_input = parser.parse_id("_0x202")
    assert (block_input, "from") in sample.nodes[pushbutton].links
    assert (pushbutton, "to") in sample.nodes[block_input].links


def test_scene_relay_link_points_at_owner_of_target_link(sample, parser):
    scene = parser.parse_id("_0x204")
    lamp_on = parser.parse_id("_0x111")
    assert (lamp_on, "scene") in sample.nodes[scene].links


def test_detail_has_integer_id_path_and_link_labels(sample, parser):
    detail = sample.detail(parser.parse_id("_0x202"))
    assert detail["id"] == 514
    assert detail["id_hex"] == "0x202"
    assert [p["name"] for p in detail["path"]] == ["Køkken", "Fremkald scenarie", "Tænd scenarie"]
    assert detail["links"][0]["label"] == "Køkken / Tryk 4 tast / Tryk (øverst venstre)"


def test_detail_enum_shows_values_and_initial_name(sample, parser):
    detail = sample.detail(parser.parse_id("_0x209"))
    assert [v["name"] for v in detail["enum"]["values"]] == ["Ur 1", "Ur 2"]
    assert detail["attrs"]["inivalue"] == "Ur 2"


def test_search_by_name_and_by_id(sample, parser):
    assert [r["name"] for r in sample.search("lampeudtag")] == ["Lampeudtag"]
    by_dec = sample.search("514")
    assert any(r["id"] == 514 for r in by_dec)
    by_hex = sample.search("0x202")
    assert [r["id"] for r in by_hex] == [514]
    assert sample.search("tryk 4", "programs") == []
    assert sample.search("") == []


def test_kinds_for_live_values(sample, parser):
    assert sample.kinds([parser.parse_id("_0x207"), parser.parse_id("_0x200"), 999999]) == {
        parser.parse_id("_0x207"): "time"
    }


REAL = os.environ.get("VMI_REAL_VIS")


@pytest.mark.skipif(not REAL or not Path(REAL).exists(), reason="set VMI_REAL_VIS to a .vis file")
def test_real_project_smoke(parser):
    project = parser.Project(Path(REAL).read_bytes())
    assert project.info["resources"] > 100
    assert project.info["functionblocks"] > 0
    # every link must be symmetric
    for node in project.nodes.values():
        for target, direction in node.links:
            if direction == "scene":
                continue
            assert any(t == node.id for t, _ in project.nodes[target].links), (node.id, target)
