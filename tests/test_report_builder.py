"""Documentation reports built from the project, like the controller's own report pages."""

from __future__ import annotations

import pytest

from conftest import load_module

parser = load_module("project_parser")
rb = load_module("report_builder")

PROJECT = (
    '<utcs_project version_major="4" version_minor="0">'
    '<project_info description="Hus" programmer="Anna"/><customer_info name="Familien" city="Byen"/>'
    '<installer_info name="Elektrikeren" phone="1234"/>'
    '<documentation_modules id="_0x1"><dataline_input_modules id="_0x2">'
    '<dataline_input_module id="_0x3" module_type="Input 24" dataline="1" location="Tavle 1"/></dataline_input_modules>'
    '<dataline_output_modules id="_0x4"/></documentation_modules>'
    '<group id="_0x10" name="Køkken">'
    '<product_dataline id="_0x11" name="Tryk 2 tast" position="Ved døren" cabletype="LINK-10" cablenumber="7" power_group="Gruppe 1" enduser_report="yes">'
    '<dataline_input id="_0x12" name="Venstre" address_dataline="_0x1" cable_colour="hvid"><link_from_resource id="_0x13" link="_0x33"/></dataline_input>'
    '<dataline_input id="_0x14" name="Højre" address_dataline="_0x9"><link_from_resource id="_0x15" link="_0x36"/></dataline_input>'
    '<dataline_output id="_0x16" name="LED" address_dataline="_0x0"/></product_dataline>'
    '<product_dataline id="_0x17" name="Udtag" position="Bord"><dataline_output id="_0x18" name="Relæ" address_dataline="_0xa"/></product_dataline>'
    '<functionblock id="_0x30" name="Lys" note="Køkkenlys"><inputs id="_0x31">'
    '<resource_input id="_0x32" name="Tænd/sluk" note="Tænder og slukker loftlyset"><link_to_resource id="_0x33" link="_0x13"/></resource_input>'
    "</inputs><settings id=\"_0x34\">"
    '<resource_timer id="_0x35" name="Efterløb" hour="0" minute="5" second="0" millisecond="250"/></settings>'
    '<internalsettings id="_0x40"><resource_flag id="_0x41" name="Hjælp" inivalue="on"/></internalsettings></functionblock>'
    "</group>"
    '<group id="_0x50" name="Stue"><functionblock id="_0x51" name="Scene"><inputs id="_0x52">'
    '<resource_input id="_0x36" name="Start"><link_to_resource id="_0x37" link="_0x15"/></resource_input></inputs></functionblock></group>'
    "</utcs_project>"
)


@pytest.fixture(scope="module")
def project():
    return parser.Project(PROJECT)


@pytest.mark.parametrize(("address", "divider", "label"), [
    (1, 16, "1.01"), (8, 16, "1.08"), (9, 16, "1.11"), (16, 16, "1.18"), (17, 16, "2.01"), (9, 8, "2.01"), (0, 16, "?"),
])
def test_terminals_are_numbered_like_the_ihc_modules(address, divider, label):
    assert rb.terminal(address, divider) == label


def test_installation_lists_inputs_outputs_modules_and_products(project):
    r = rb.installation(project)
    assert r["documentation"]["installer"] == {"name": "Elektrikeren", "phone": "1234"}
    assert [(i["terminal"], i["name"], i["product"], i["location"], i["cabletype"], i["colour"]) for i in r["inputs"]] == [
        ("1.01", "Venstre", "Tryk 2 tast", "Køkken", "LINK-10", "hvid"), ("1.11", "Højre", "Tryk 2 tast", "Køkken", "LINK-10", "")]
    assert [o["terminal"] for o in r["outputs"]] == ["2.02", "?"]  # not connected last
    assert r["input_modules"] == [{"line": 1, "type": "Input 24", "location": "Tavle 1"}]
    first = next(p for p in r["products"] if p["name"] == "Tryk 2 tast")
    assert [(t["direction"], t["terminal"]) for t in first["terminals"]] == [("in", "1.01"), ("in", "1.11"), ("out", "?")]


def test_function_documentation_tells_what_each_button_does(project):
    r = rb.function(project)
    assert [g["name"] for g in r["groups"]] == ["Køkken"] and r["marked_any"]
    product = r["groups"][0]["products"][0]
    does = {i["name"]: i["does"] for i in product["inputs"]}
    assert does["Venstre"] == [{"text": "Tænder og slukker loftlyset", "where": "", "id": 0x32}]
    # no note on the target: block and input name instead, and the block's location since it is elsewhere
    assert does["Højre"][0]["text"] == "Scene: Start" and does["Højre"][0]["where"] == "Stue"
    assert len(rb.function(project, only_marked=False)["groups"][0]["products"]) == 2


def test_function_block_documentation_leaves_out_internal_settings(project):
    blocks = {b["name"]: b for b in rb.functionblocks(project)["blocks"]}
    light = blocks["Lys"]
    assert light["note"] == "Køkkenlys" and light["location"] == "Køkken"
    assert [s["key"] for s in light["sections"]] == ["inputs", "settings"]
    timer = light["sections"][1]["resources"][0]
    assert (timer["name"], timer["initial"]) == ("Efterløb", "00:05:00,250")
    assert light["sections"][0]["resources"][0]["links"][0]["label"] == "Køkken / Tryk 2 tast / Venstre"


def test_documentation_details_never_reach_the_project_info(project):
    assert "Elektrikeren" not in repr(project.info) and "Familien" not in repr(project.info)
